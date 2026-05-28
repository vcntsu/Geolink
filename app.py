"""
app.py — GeoLink Calc v2.1
Ejecutar: streamlit run app.py
"""
import streamlit as st
import numpy as np

st.set_page_config(
    page_title="GeoLink Calc",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import CSS, render_header, render_status, render_kpi_row
from components import (render_sidebar, render_kpi_panel, render_panel_derivada,
                        render_panel_integral, render_calculadora_simbolica,
                        render_presupuesto, render_analisis_sensibilidad)
from terrain_engine import (LinkParameters, ObstacleParameters,
                             calcular_perfil_completo, calcular_presupuesto_enlace,
                             calcular_curvatura_tierra, calcular_carga_viento,
                             generar_recomendaciones)
from charts import grafico_perfil_enlace, grafico_derivada_terreno, grafico_radio_fresnel
from math_engine import get_terrain_derivative_analysis

# ── CSS global ──────────────────────────────────────────────────────────────
st.markdown(CSS, unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(render_header(), unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
p = render_sidebar()

# ── Domain objects ───────────────────────────────────────────────────────────
link = LinkParameters(
    distancia_km=p["distancia"],
    frecuencia_ghz=p["frecuencia"],
    altura_antena_a=p["altura_a"],
    altura_antena_b=p["altura_b"],
    potencia_tx_dbm=p["potencia_tx"],
    ganancia_antena_db=p["ganancia"],
    sensibilidad_rx_dbm=p["sensibilidad"],
)

obstaculos = [ObstacleParameters(p["h1"], p["p1"], p["a1"], p["t1"])]
if p["usar2"]:
    obstaculos.append(ObstacleParameters(p["h2"], p["p2"], p["a2"], p["t2"]))

# ── Core calculations ────────────────────────────────────────────────────────
perfil = calcular_perfil_completo(link, obstaculos, n_puntos=p["n_pts"])
perdidas = calcular_presupuesto_enlace(link, perfil)
viento = calcular_carga_viento(p["viento_vel"], p["torre_altura"], p["torre_diametro"])
recomendaciones = generar_recomendaciones(link, perfil, perdidas, viento)

# ── Distance warning ─────────────────────────────────────────────────────────
if link.distancia_km > 100:
    st.warning(
        f"⚠️ Distancia de {link.distancia_km:.0f} km excede el rango típico de Ubiquiti. "
        "Los resultados son orientativos."
    )

# ── Status banner ────────────────────────────────────────────────────────────
st.markdown(
    render_status(perfil.viable, perfil.area_obstruccion,
                  perfil.clearance_minimo, perdidas.margen_enlace_db),
    unsafe_allow_html=True,
)

# ── KPI cards ────────────────────────────────────────────────────────────────
render_kpi_panel(perfil, perdidas, link)
st.markdown("<hr class='gl-divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ════════════════════════════════════════════════════════════════════════════
tab_sim, tab_calc, tab_report = st.tabs([
    "🗺️ Simulador en Vivo",
    "🧮 Calculadora Matemática",
    "📊 Análisis y Reporte",
])

# ── TAB 1: SIMULADOR EN VIVO ─────────────────────────────────────────────────
with tab_sim:
    fig_p = grafico_perfil_enlace(
        perfil, link,
        mostrar_r1=p["mostrar_r1"],
        mostrar_r06=p["mostrar_r06"],
    )
    st.plotly_chart(fig_p, width="stretch")

    if p["mostrar_curv"] and link.distancia_km > 10:
        curv = calcular_curvatura_tierra(perfil.x, link.distancia_km)
        curv_max = float(np.max(curv)) * 1000
        st.info(
            f"🌍 Curvatura terrestre máxima en el centro: **{curv_max:.2f} m** "
            f"({'significativa' if curv_max > 5 else 'despreciable'} para este enlace)"
        )

    col_d, col_i = st.columns(2, gap="large")
    with col_d:
        with st.expander("📐 Análisis Diferencial del Terreno", expanded=True):
            render_panel_derivada(perfil)
            an = get_terrain_derivative_analysis(perfil.elevacion, perfil.x)
            fig_d = grafico_derivada_terreno(
                perfil.x, perfil.elevacion,
                an["primera_deriv"], an["segunda_deriv"],
            )
            st.plotly_chart(fig_d, width="stretch")

    with col_i:
        with st.expander("∫ Integral de Obstrucción", expanded=True):
            render_panel_integral(perfil)
        with st.expander("📶 Radio de Fresnel vs Frecuencia"):
            st.plotly_chart(grafico_radio_fresnel(perfil.x, link), width="stretch")
            st.caption("Mayor frecuencia → menor radio de Fresnel → más fácil despejar, pero mayor FSPL.")

# ── TAB 2: CALCULADORA MATEMÁTICA ────────────────────────────────────────────
with tab_calc:
    render_calculadora_simbolica()

# ── TAB 3: ANÁLISIS Y REPORTE ────────────────────────────────────────────────
with tab_report:
    col_rec, col_rf = st.columns([3, 2], gap="large")
    with col_rec:
        from components import render_recomendaciones
        render_recomendaciones(recomendaciones, viento, link, perdidas)
    with col_rf:
        render_presupuesto(perdidas)

    st.markdown("<hr class='gl-divider'>", unsafe_allow_html=True)
    render_analisis_sensibilidad(link, obstaculos)

    st.markdown("<hr class='gl-divider'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 📡 Zona de Fresnel")
        st.latex(r"r_1 = 17.32\,\sqrt{\frac{d_1 \cdot d_2}{f \cdot D}}")
        st.markdown("$d_1, d_2$ en km · $f$ en GHz · $D$ distancia total en km")
        st.markdown("##### 📉 Free Space Path Loss")
        st.latex(r"\text{FSPL} = 20\log_{10}(d) + 20\log_{10}(f) + 92.45\;\text{dB}")
        st.markdown("##### 📐 Presupuesto RF")
        st.latex(r"P_{RX} = P_{TX} + G_{TX} - \text{FSPL} - L_{dif} + G_{RX}")
    with c2:
        st.markdown("##### ∫ Integral de Obstrucción")
        st.latex(r"A_{obs} = \int_{0}^{D} \max\!\left(0,\; h(x) - F_{inf}(x)\right) dx")
        st.markdown("##### 🌬️ Carga de Viento")
        st.latex(r"F = \frac{1}{2} C_d \cdot \rho \cdot A \cdot v^2")
        st.markdown("##### 🔗 Criterios Ubiquiti")
        import pandas as pd
        df = pd.DataFrame({
            "Parámetro": ["Zona de Fresnel", "RSSI mínimo", "Margen enlace", "Potencia TX"],
            "Criterio": ["≥ 60% de R₁ despejado", "> −80 dBm", "> 15 dB", "≤ 23 dBm (ISM)"],
        })
        st.dataframe(df, width="stretch", hide_index=True)

    st.markdown(
        "<div style='text-align:center;color:#9CA3AF;font-size:0.75rem;padding:24px 0 8px'>"
        "GeoLink Calc v2.1 · Proyecto Cálculo Integral · 2026 · "
        "<span style='color:#F59E0B'>■</span> Fresnel R₁ &nbsp;"
        "<span style='color:#007AFF'>■</span> Fresnel R₀.₆ &nbsp;"
        "<span style='color:#27AE60'>■</span> Terreno &nbsp;"
        "<span style='color:#E74C3C'>■</span> Obstrucción"
        "</div>",
        unsafe_allow_html=True,
    )
