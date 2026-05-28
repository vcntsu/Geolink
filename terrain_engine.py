"""
terrain_engine.py — Motor de modelado del terreno y Zona de Fresnel
"""
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class LinkParameters:
    distancia_km: float
    frecuencia_ghz: float
    altura_antena_a: float
    altura_antena_b: float
    potencia_tx_dbm: float = 23.0
    ganancia_antena_db: float = 23.0
    sensibilidad_rx_dbm: float = -90.0


@dataclass
class ObstacleParameters:
    altura_m: float
    posicion_km: float
    ancho_km: float
    tipo: str = "gaussiano"


@dataclass
class TerrainProfile:
    x: np.ndarray
    elevacion: np.ndarray
    linea_vista: np.ndarray
    fresnel_r1_superior: np.ndarray
    fresnel_r1_inferior: np.ndarray
    fresnel_r06_superior: np.ndarray
    fresnel_r06_inferior: np.ndarray
    obstruccion_mask: np.ndarray
    area_obstruccion: float
    clearance_minimo: float
    viable: bool
    margen_db: float


@dataclass
class PropagationLoss:
    fspl_db: float
    perdida_difraccion_db: float
    perdida_total_db: float
    potencia_rx_dbm: float
    margen_enlace_db: float
    viable: bool
    rssi_estimado: str


def _trapezoid(y, x):
    """Wrapper compatible con NumPy 1.x y 2.x"""
    if hasattr(np, 'trapezoid'):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def generar_terreno(link: LinkParameters, obstaculos: List[ObstacleParameters],
                    n_puntos: int = 600) -> Tuple[np.ndarray, np.ndarray]:
    x = np.linspace(0, link.distancia_km, n_puntos)
    terreno = np.zeros(n_puntos)

    for obs in obstaculos:
        sigma = max(obs.ancho_km / 2.5, 0.01)
        if obs.tipo == "gaussiano":
            comp = obs.altura_m * np.exp(-((x - obs.posicion_km) / sigma) ** 2)
        elif obs.tipo == "triangular":
            dist = np.abs(x - obs.posicion_km)
            comp = np.maximum(0, obs.altura_m * (1 - dist / max(obs.ancho_km / 2, 0.01)))
        elif obs.tipo == "rectangular":
            comp = np.where(np.abs(x - obs.posicion_km) <= obs.ancho_km / 2, obs.altura_m, 0.0)
        elif obs.tipo == "doble_pico":
            off = obs.ancho_km / 3
            p1 = obs.altura_m * np.exp(-((x - (obs.posicion_km - off)) / (sigma * 0.6)) ** 2)
            p2 = obs.altura_m * 0.85 * np.exp(-((x - (obs.posicion_km + off)) / (sigma * 0.6)) ** 2)
            comp = p1 + p2
        else:
            comp = obs.altura_m * np.exp(-((x - obs.posicion_km) / sigma) ** 2)
        terreno += comp

    try:
        from scipy.ndimage import gaussian_filter1d
        terreno = gaussian_filter1d(terreno, sigma=2)
    except Exception:
        pass

    return x, terreno


def calcular_linea_vista(x: np.ndarray, link: LinkParameters) -> np.ndarray:
    return link.altura_antena_a + (
        (link.altura_antena_b - link.altura_antena_a) / link.distancia_km
    ) * x


def calcular_radio_fresnel(x: np.ndarray, link: LinkParameters, coef: float = 1.0) -> np.ndarray:
    d1 = np.clip(x, 1e-6, None)
    d2 = np.clip(link.distancia_km - x, 1e-6, None)
    return coef * 17.32 * np.sqrt((d1 * d2) / (link.frecuencia_ghz * link.distancia_km))


def calcular_perfil_completo(link: LinkParameters, obstaculos: List[ObstacleParameters],
                              n_puntos: int = 600) -> TerrainProfile:
    x, terreno = generar_terreno(link, obstaculos, n_puntos)
    los = calcular_linea_vista(x, link)
    r1 = calcular_radio_fresnel(x, link, 1.0)
    r06 = calcular_radio_fresnel(x, link, 0.6)

    fr1_sup = los + r1
    fr1_inf = los - r1
    fr06_sup = los + r06
    fr06_inf = los - r06

    obs_y = np.maximum(0, terreno - fr06_inf)
    obs_mask = obs_y > 0
    # x is in km, obs_y in meters → result is m·km → multiply by 1000 to get m²
    area_obs = _trapezoid(obs_y, x) * 1000.0

    clearance = fr06_inf - terreno
    clearance_min = float(np.min(clearance))
    viable = area_obs == 0.0
    margen = clearance_min * 0.5

    return TerrainProfile(
        x=x, elevacion=terreno, linea_vista=los,
        fresnel_r1_superior=fr1_sup, fresnel_r1_inferior=fr1_inf,
        fresnel_r06_superior=fr06_sup, fresnel_r06_inferior=fr06_inf,
        obstruccion_mask=obs_mask, area_obstruccion=area_obs,
        clearance_minimo=clearance_min, viable=viable, margen_db=margen
    )


def calcular_fspl(distancia_km: float, frecuencia_ghz: float) -> float:
    return 20 * np.log10(distancia_km) + 20 * np.log10(frecuencia_ghz) + 92.45


def calcular_perdida_difraccion(area_obs: float, clearance_min: float) -> float:
    """ITU-R knife-edge diffraction. clearance_min < 0 means obstruction (meters)."""
    if area_obs == 0 or clearance_min >= 0:
        return 0.0
    v = abs(clearance_min) / 15.0
    return max(0.0, 6.02 + 9.11 * v + 1.27 * v ** 2)


def calcular_presupuesto_enlace(link: LinkParameters, perfil: TerrainProfile) -> PropagationLoss:
    # PRX = PTX + GainTX - FSPL - Ldif + GainRX
    fspl = calcular_fspl(link.distancia_km, link.frecuencia_ghz)
    pdif = calcular_perdida_difraccion(perfil.area_obstruccion, perfil.clearance_minimo)
    ptotal = fspl + pdif
    prx = link.potencia_tx_dbm + link.ganancia_antena_db - ptotal + link.ganancia_antena_db
    margen = prx - link.sensibilidad_rx_dbm
    viable = margen > 0

    if prx > -60:
        rssi = "Excelente (> -60 dBm)"
    elif prx > -70:
        rssi = "Muy bueno (-60 a -70 dBm)"
    elif prx > -80:
        rssi = "Bueno (-70 a -80 dBm)"
    elif prx > -90:
        rssi = "Marginal (-80 a -90 dBm)"
    else:
        rssi = "Insuficiente (< -90 dBm)"

    return PropagationLoss(
        fspl_db=fspl, perdida_difraccion_db=pdif, perdida_total_db=ptotal,
        potencia_rx_dbm=prx, margen_enlace_db=margen, viable=viable, rssi_estimado=rssi
    )


def analisis_sensibilidad_frecuencia(link: LinkParameters,
                                      obstaculos: List[ObstacleParameters],
                                      freqs: List[float]) -> dict:
    res = {'frecuencias': [], 'radio_fresnel_max': [], 'area_obs': [], 'viable': [], 'fspl': []}
    for f in freqs:
        lt = LinkParameters(link.distancia_km, f, link.altura_antena_a, link.altura_antena_b,
                            link.potencia_tx_dbm, link.ganancia_antena_db, link.sensibilidad_rx_dbm)
        p = calcular_perfil_completo(lt, obstaculos)
        res['frecuencias'].append(round(f, 2))
        res['radio_fresnel_max'].append(float(np.max(calcular_radio_fresnel(p.x, lt))))
        res['area_obs'].append(p.area_obstruccion)
        res['viable'].append(p.viable)
        res['fspl'].append(calcular_fspl(link.distancia_km, f))
    return res


def analisis_altura_optima(link: LinkParameters, obstaculos: List[ObstacleParameters],
                            alturas: List[float], antena: str = 'A') -> dict:
    res = {'alturas': [], 'area_obs': [], 'viable': [], 'clearance': []}
    for h in alturas:
        if antena == 'A':
            lt = LinkParameters(link.distancia_km, link.frecuencia_ghz, h, link.altura_antena_b,
                                link.potencia_tx_dbm, link.ganancia_antena_db, link.sensibilidad_rx_dbm)
        else:
            lt = LinkParameters(link.distancia_km, link.frecuencia_ghz, link.altura_antena_a, h,
                                link.potencia_tx_dbm, link.ganancia_antena_db, link.sensibilidad_rx_dbm)
        p = calcular_perfil_completo(lt, obstaculos)
        res['alturas'].append(h)
        res['area_obs'].append(p.area_obstruccion)
        res['viable'].append(p.viable)
        res['clearance'].append(p.clearance_minimo)
    return res


def calcular_curvatura_tierra(x: np.ndarray, distancia_km: float) -> np.ndarray:
    d1 = x
    d2 = distancia_km - x
    return (d1 * d2) / (2 * 8500.0)


def calcular_carga_viento(velocidad_kmh: float, altura_torre_m: float,
                           diametro_mm: float) -> dict:
    """F = 0.5 * Cd * rho * A * v²  (Cd=1.2, rho=1.225 kg/m³)"""
    v_ms = velocidad_kmh / 3.6
    Cd, rho = 1.2, 1.225
    area = altura_torre_m * (diametro_mm / 1000.0)
    fuerza_n = 0.5 * Cd * rho * area * v_ms ** 2
    fuerza_kg = fuerza_n / 9.81
    momento_nm = fuerza_n * (altura_torre_m / 2)
    limite_n = 800 * (diametro_mm / 50) ** 2 * (3.0 / max(altura_torre_m, 1))
    seguro = fuerza_n <= limite_n
    v_max_ms = np.sqrt(limite_n / max(0.5 * Cd * rho * area, 1e-9))
    return {
        'fuerza_n': fuerza_n, 'fuerza_kg': fuerza_kg,
        'momento_nm': momento_nm, 'seguro': seguro,
        'v_max_kmh': v_max_ms * 3.6, 'limite_n': limite_n,
    }


def generar_recomendaciones(link: LinkParameters, perfil: TerrainProfile,
                             perdidas: PropagationLoss, viento: dict) -> dict:
    recs = []
    score = 100

    if not perfil.viable:
        pen = abs(perfil.clearance_minimo)
        h_min_a = link.altura_antena_a + pen + 3
        h_min_b = link.altura_antena_b + pen + 3
        r06_max = float(np.max(calcular_radio_fresnel(perfil.x, link, 0.6)))
        f_new = min(link.frecuencia_ghz * (r06_max / max(r06_max - pen, 1)) ** 2, 6.0)
        recs.append({
            'tipo': 'error',
            'titulo': '📡 Obstrucción de Fresnel detectada',
            'detalle': [
                f"Sube Antena A a **{h_min_a:.0f} m** (actual: {link.altura_antena_a:.0f} m)",
                f"O sube Antena B a **{h_min_b:.0f} m** (actual: {link.altura_antena_b:.0f} m)",
                f"O aumenta frecuencia a **{f_new:.1f} GHz** para reducir radio de Fresnel",
                f"Penetración actual: **{pen:.1f} m** en zona de Fresnel 60%",
            ]
        })
        score -= min(50, int(pen * 3))

    if perdidas.margen_enlace_db < 0:
        score -= 30
        recs.append({
            'tipo': 'error',
            'titulo': '📉 Margen de enlace negativo',
            'detalle': [
                f"Margen: **{perdidas.margen_enlace_db:.1f} dB** (mínimo: +15 dB)",
                f"RSSI estimado: **{perdidas.potencia_rx_dbm:.1f} dBm**",
                "Aumenta ganancia de antenas o reduce distancia",
            ]
        })
    elif perdidas.margen_enlace_db < 15:
        score -= 15
        recs.append({
            'tipo': 'warning',
            'titulo': '⚠️ Margen de enlace bajo',
            'detalle': [
                f"Margen: **{perdidas.margen_enlace_db:.1f} dB** — recomendado > 15 dB",
                "Considera antenas de mayor ganancia o reducir pérdidas de cable",
            ]
        })

    if not viento['seguro']:
        score -= 20
        recs.append({
            'tipo': 'warning',
            'titulo': '🌬️ Riesgo estructural por viento',
            'detalle': [
                f"Velocidad máxima segura: **{viento['v_max_kmh']:.0f} km/h**",
                f"Fuerza actual: **{viento['fuerza_kg']:.1f} kg** sobre la torre",
                "Usa tirantes a 120° a 2/3 de la altura del mástil",
            ]
        })

    if link.distancia_km > 60:
        score -= 10
        recs.append({
            'tipo': 'warning',
            'titulo': '📏 Enlace de larga distancia',
            'detalle': [
                f"A {link.distancia_km:.0f} km la curvatura terrestre es significativa",
                "Considera repetidor intermedio para mejorar confiabilidad",
            ]
        })

    if not recs:
        recs.append({
            'tipo': 'success',
            'titulo': '✅ Instalación óptima',
            'detalle': [
                f"Margen de enlace: **+{perdidas.margen_enlace_db:.1f} dB** — excelente",
                "Zona de Fresnel completamente despejada",
                f"RSSI: **{perdidas.potencia_rx_dbm:.1f} dBm** — {perdidas.rssi_estimado}",
            ]
        })

    return {'recomendaciones': recs, 'score': max(0, min(100, score))}
