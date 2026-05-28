"""
components.py — Componentes de UI para GeoLink Calc
"""
import streamlit as st
import numpy as np
from math_engine import (compute_derivative, compute_integral,
                          get_terrain_derivative_analysis, taylor_expansion,
                          riemann_sum)
from terrain_engine import TerrainProfile, PropagationLoss, LinkParameters
from styles import render_kpi_row, render_status


def render_sidebar() -> dict:
    st.sidebar.markdown(
        "<div style='font-size:1rem;font-weight:700;color:#111827;padding:4px 0 12px'>⚙️ Parámetros del Enlace</div>",
        unsafe_allow_html=True
    )

    with st.sidebar.expander("📡 Antenas y Distancia", expanded=True):
        distancia = st.slider("Distancia del enlace (km)", 1.0, 150.0, 20.0, 0.5,
                              help="Distancia en línea recta entre las dos antenas")
        frecuencia = st.slider("Frecuencia (GHz)", 2.4, 6.0, 5.0, 0.1,
                               help="Frecuencia de operación. Mayor frecuencia = menor radio de Fresnel pero mayor FSPL")
        altura_a = st.slider("Altura Antena A — TX (m)", 5, 150, 40,
                             help="Altura sobre el suelo de la antena transmisora")
        altura_b = st.slider("Altura Antena B — RX (m)", 5, 150, 35,
                             help="Altura sobre el suelo de la antena receptora")

    with st.sidebar.expander("📻 Parámetros RF", expanded=False):
        potencia_tx = st.slider("Potencia TX (dBm)", 10, 30, 23,
                                help="Potencia de transmisión. Ubiquiti típico: 23 dBm (ISM limit)")
        ganancia = st.slider("Ganancia antena (dBi)", 10, 35, 23,
                             help="Ganancia de cada antena. Se aplica en TX y RX")
        sensibilidad = st.slider("Sensibilidad RX (dBm)", -100, -60, -90,
                                 help="Sensibilidad mínima del receptor. Ubiquiti típico: -75 a -90 dBm")

    with st.sidebar.expander("⛰️ Obstáculo 1", expanded=True):
        h1 = st.slider("Altura del cerro (m)", 0, 150, 45,
                       help="Altura máxima del obstáculo sobre el nivel de referencia")
        p1 = st.slider("Posición (km)", 1.0, max(distancia - 1.0, 1.1), distancia / 2, 0.5,
                       help="Posición del obstáculo a lo largo del enlace")
        a1 = st.slider("Ancho del cerro (km)", 0.5, 15.0, 4.0, 0.5,
                       help="Ancho a media altura del obstáculo")
        t1 = st.selectbox("Forma", ["gaussiano", "triangular", "rectangular", "doble_pico"], key="t1",
                          help="Perfil del obstáculo")

    with st.sidebar.expander("⛰️ Obstáculo 2 (opcional)", expanded=False):
        usar2 = st.checkbox("Activar segundo obstáculo", value=False)
        h2 = st.slider("Altura cerro 2 (m)", 0, 150, 30, disabled=not usar2)
        p2 = st.slider("Posición cerro 2 (km)", 1.0, max(distancia - 1.0, 1.1),
                        min(distancia * 0.75, distancia - 1.0), 0.5, disabled=not usar2)
        a2 = st.slider("Ancho cerro 2 (km)", 0.5, 15.0, 3.0, 0.5, disabled=not usar2)
        t2 = st.selectbox("Forma 2", ["gaussiano", "triangular", "rectangular", "doble_pico"],
                           key="t2", disabled=not usar2)

    with st.sidebar.expander("🌬️ Análisis de Viento", expanded=False):
        viento_vel = st.slider("Velocidad del viento (km/h)", 0, 200, 80,
                               help="Velocidad de diseño del viento para cálculo estructural")
        torre_altura = st.slider("Altura de la torre (m)", 3, 60, 10,
                                 help="Altura total del mástil o torre de soporte")
        torre_diametro = st.number_input("Diámetro del mástil (mm)", min_value=20, max_value=200,
                                         value=50, step=5,
                                         help="Diámetro exterior del tubo del mástil")

    with st.sidebar.expander("🎨 Visualización", expanded=False):
        mostrar_r1 = st.checkbox("Fresnel R₁ (100%)", value=True)
        mostrar_r06 = st.checkbox("Fresnel R₀.₆ (60%)", value=True)
        mostrar_curv = st.checkbox("Curvatura terrestre", value=False)
        n_pts = st.select_slider("Resolución", options=[200, 400, 600, 800], value=600)

    st.sidebar.markdown(
        "<div style='font-size:0.72rem;color:#6B7280;text-align:center;"
        "padding-top:16px;border-top:1px solid #E5E7EB;margin-top:12px'>"
        "GeoLink Calc v2.1 · SymPy + Plotly<br>Proyecto Cálculo Integral · 2026</div>",
        unsafe_allow_html=True
    )

    return dict(distancia=distancia, frecuencia=frecuencia, altura_a=altura_a, altura_b=altura_b,
                potencia_tx=potencia_tx, ganancia=ganancia, sensibilidad=sensibilidad,
                h1=h1, p1=p1, a1=a1, t1=t1,
                usar2=usar2, h2=h2, p2=p2, a2=a2, t2=t2,
                viento_vel=viento_vel, torre_altura=torre_altura, torre_diametro=float(torre_diametro),
                mostrar_r1=mostrar_r1, mostrar_r06=mostrar_r06,
                mostrar_curv=mostrar_curv, n_pts=n_pts)


def render_kpi_panel(perfil: TerrainProfile, perdidas: PropagationLoss, link: LinkParameters):
    items = [
        (f"{link.distancia_km:.1f} km",        "Distancia",        "blue"),
        (f"{link.frecuencia_ghz:.1f} GHz",      "Frecuencia",       "orange"),
        (f"{perdidas.fspl_db:.1f} dB",           "FSPL",             "purple"),
        (f"{perdidas.potencia_rx_dbm:.1f} dBm",  "Potencia RX",      "cyan"),
        (f"{perdidas.margen_enlace_db:.1f} dB",  "Margen enlace",
         "green" if perdidas.viable else "red"),
        (f"{perfil.area_obstruccion:.1f} m²",    "Área obstrucción",
         "green" if perfil.viable else "red"),
    ]
    st.markdown(render_kpi_row(items), unsafe_allow_html=True)


def render_panel_derivada(perfil: TerrainProfile):
    st.markdown("#### 📐 Derivada del Terreno")
    an = get_terrain_derivative_analysis(perfil.elevacion, perfil.x)

    c1, c2 = st.columns(2)
    c1.metric("Posición de la cumbre", f"{an['x_max_altura']:.2f} km")
    c2.metric("Altura máxima", f"{an['y_max_altura']:.1f} m")

    st.info(
        f"En la cumbre (x = {an['x_max_altura']:.2f} km), "
        f"$h'(x) \\approx {an['pendiente_en_max']:.4f}$ m/km ≈ 0 → **punto crítico máximo**"
    )

    c3, c4 = st.columns(2)
    c3.metric("Pendiente máx. (+)", f"{an['pendiente_max_pos']:.2f} m/km",
              help=f"En x = {an['x_max_pendiente_pos']:.2f} km")
    c4.metric("Pendiente máx. (−)", f"{an['pendiente_max_neg']:.2f} m/km",
              help=f"En x = {an['x_max_pendiente_neg']:.2f} km")

    with st.expander("¿Qué significa la derivada aquí?"):
        st.markdown("""
        $h'(x) = \\dfrac{dh}{dx}$ mide la **razón de cambio instantánea** de la altura:

        - $h'(x) > 0$ → terreno **sube**
        - $h'(x) < 0$ → terreno **baja**
        - $h'(x) = 0$ → **cumbre** del obstáculo (punto crítico)

        La cumbre es el punto más crítico para la obstrucción de la Zona de Fresnel.
        """)


def render_panel_integral(perfil: TerrainProfile):
    st.markdown("#### ∫ Integral de Obstrucción")
    st.latex(r"A_{obs} = \int_{0}^{D} \max\!\left(0,\; h(x) - F_{inf}(x)\right) dx")

    c1, c2, c3 = st.columns(3)
    color_a = "red" if perfil.area_obstruccion > 0 else "green"
    color_c = "red" if perfil.clearance_minimo < 0 else "green"
    c1.metric("Área obstrucción", f"{perfil.area_obstruccion:.2f} m²")
    c2.metric("Clearance mínimo", f"{perfil.clearance_minimo:.2f} m")
    pct = 100 if perfil.area_obstruccion == 0 else max(0, 100 - perfil.area_obstruccion * 10)
    c3.metric("Zona despejada", f"{pct:.0f}%")

    if perfil.area_obstruccion > 0:
        st.error(
            f"Obstrucción de **{perfil.area_obstruccion:.2f} m²** detectada. "
            f"El terreno penetra **{abs(perfil.clearance_minimo):.1f} m** en la zona de Fresnel."
        )
        st.markdown(f"**Soluciones:** aumentar antenas ≥ {abs(perfil.clearance_minimo)+5:.0f} m · "
                    "reducir frecuencia · reubicar antenas · instalar repetidor")
    else:
        st.success("Zona de Fresnel completamente despejada. Integral de obstrucción = 0.")

    with st.expander("¿Qué mide esta integral?"):
        st.markdown("""
        La integral acumula el área donde el terreno supera el límite inferior del 60% de Fresnel.
        Cuanto mayor sea $A_{obs}$, mayores son las pérdidas por difracción.

        Se evalúa numéricamente con la **Regla del Trapecio**:
        $$\\int_a^b f(x)\\,dx \\approx \\frac{\\Delta x}{2}\\sum_{i=0}^{n-1}[f(x_i)+f(x_{i+1})]$$
        """)


def render_calculadora_simbolica():
    st.markdown("#### 🧮 Calculadora Simbólica")
    st.caption("Ingresa cualquier función y calcula derivada, integral, Taylor o Riemann paso a paso.")

    tab_d, tab_i, tab_t, tab_r = st.tabs(["📐 Derivada", "∫ Integral", "📈 Taylor", "📊 Riemann"])

    # ── Derivada ──
    with tab_d:
        c1, c2 = st.columns([3, 1])
        with c1:
            fd = st.text_input("f(x) =", value="x**3 - 4*x**2 + 2*x - 1", key="fd",
                               help="Usa: sin(x), cos(x), exp(x), log(x), sqrt(x), x**n")
        with c2:
            xd = st.number_input("Evaluar en x =", value=2.0, step=0.5, key="xd")

        if st.button("Calcular Derivada", key="btn_d", use_container_width=True):
            with st.spinner("Calculando con SymPy..."):
                r = compute_derivative(fd, eval_point=xd)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Función original:**")
                try:
                    st.latex(f"f(x) = {r.latex_original}")
                except Exception:
                    st.code(r.original_expr)
            with col_b:
                st.markdown("**Derivada:**")
                try:
                    st.latex(f"f'(x) = {r.latex_derivative}")
                except Exception:
                    st.code(r.derivative_expr)

            if r.slope_value is not None:
                st.metric(f"f'({xd})", f"{r.slope_value:.6f}")

            if r.critical_points:
                st.markdown("**Puntos críticos:** " +
                            " · ".join([f"x = {p:.4f}" for p in r.critical_points]))

            st.markdown("**Pasos:**")
            for step in r.steps:
                st.markdown(f'<div class="gl-step">{step}</div>', unsafe_allow_html=True)

            # Gráfico
            try:
                import sympy as sp
                from math_engine import parse_function
                expr, _ = parse_function(fd)
                if expr is not None:
                    x_p = np.linspace(xd - 5, xd + 5, 400)
                    f_l = sp.lambdify(sp.Symbol('x'), expr, 'numpy')
                    df_l = sp.lambdify(sp.Symbol('x'), sp.diff(expr, sp.Symbol('x')), 'numpy')
                    yp = np.clip(np.array(f_l(x_p), dtype=float), -1e4, 1e4)
                    dyp = np.clip(np.array(df_l(x_p), dtype=float), -1e4, 1e4)
                    # Integral acumulada numérica
                    iyp = np.zeros_like(yp)
                    for k in range(1, len(x_p)):
                        iyp[k] = iyp[k-1] + (yp[k-1] + yp[k]) / 2 * (x_p[k] - x_p[k-1])
                    from charts import grafico_funcion_personalizada
                    fig = grafico_funcion_personalizada(x_p, yp, dyp, iyp, fd)
                    st.plotly_chart(fig, width='stretch')
            except Exception:
                pass

    # ── Integral ──
    with tab_i:
        c1, c2 = st.columns([3, 1])
        with c1:
            fi = st.text_input("f(x) =", value="3*x**2 - 8*x + 2", key="fi")
        with c2:
            usar_lim = st.checkbox("Integral definida", value=True, key="ul")
            la = st.number_input("Límite a", value=0.0, step=0.5, key="la", disabled=not usar_lim)
            lb = st.number_input("Límite b", value=3.0, step=0.5, key="lb", disabled=not usar_lim)

        if st.button("Calcular Integral", key="btn_i", use_container_width=True):
            with st.spinner("Calculando con SymPy..."):
                r = compute_integral(fi, lower=la if usar_lim else None,
                                     upper=lb if usar_lim else None)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Función original:**")
                try:
                    st.latex(f"f(x) = {r.latex_original}")
                except Exception:
                    st.code(r.original_expr)
            with col_b:
                st.markdown("**Antiderivada:**")
                try:
                    st.latex(f"F(x) = {r.latex_integral} + C")
                except Exception:
                    st.code(r.integral_expr)

            if r.definite_value is not None:
                st.metric(f"∫ f(x)dx en [{la}, {lb}]", f"{r.definite_value:.6f}")

            st.markdown("**Pasos:**")
            for step in r.steps:
                st.markdown(f'<div class="gl-step">{step}</div>', unsafe_allow_html=True)

    # ── Taylor ──
    with tab_t:
        c1, c2 = st.columns([3, 1])
        with c1:
            ft = st.text_input("f(x) =", value="sin(x)", key="ft")
        with c2:
            x0 = st.number_input("Punto x₀", value=0.0, step=0.5, key="x0")
            orden = st.slider("Orden", 2, 8, 4, key="ord")

        if st.button("Calcular Serie de Taylor", key="btn_t", use_container_width=True):
            with st.spinner("Calculando..."):
                r = taylor_expansion(ft, point=x0, order=orden)
            if r.get('error'):
                st.error(f"Error: {r['error']}")
            else:
                st.markdown("**Aproximación de Taylor:**")
                try:
                    st.latex(f"f(x) \\approx {r['latex']}")
                except Exception:
                    st.code(r['taylor_expr'])

                if r.get('terms'):
                    st.markdown("**Términos individuales:**")
                    cols_t = st.columns(min(len(r['terms']), 4))
                    for i, term_latex in enumerate(r['terms']):
                        with cols_t[i % len(cols_t)]:
                            st.markdown(
                                f'<div class="gl-step" style="text-align:center">'
                                f'<small style="color:#6B7280">n={i}</small><br>'
                                f'${term_latex}$</div>',
                                unsafe_allow_html=True
                            )

                st.markdown("**Pasos:**")
                for step in r['steps']:
                    st.markdown(f'<div class="gl-step">{step}</div>', unsafe_allow_html=True)

    # ── Riemann ──
    with tab_r:
        c1, c2 = st.columns([3, 1])
        with c1:
            fr = st.text_input("f(x) =", value="x**2 - 2*x + 1", key="fr")
        with c2:
            ra = st.number_input("Límite a", value=0.0, step=0.5, key="ra")
            rb = st.number_input("Límite b", value=4.0, step=0.5, key="rb")
            nr = st.slider("Rectángulos", 4, 100, 20, key="nr")
            metodo_r = st.selectbox(
                "Método", ["midpoint", "left", "right"],
                format_func=lambda m: {"midpoint": "Punto Medio", "left": "Izquierda", "right": "Derecha"}[m],
                key="metodo_r"
            )

        if st.button("Visualizar Suma de Riemann", key="btn_r", use_container_width=True):
            with st.spinner("Calculando..."):
                res_r = riemann_sum(fr, ra, rb, nr, method=metodo_r)

            if res_r.get('error'):
                st.error(f"Error: {res_r['error']}")
            else:
                ca, cb, cc = st.columns(3)
                ca.metric("Suma de Riemann", f"{res_r['suma']:.5f}")
                cb.metric("Valor exacto", f"{res_r['exacto']:.5f}")
                cc.metric("Error relativo", f"{res_r['error_pct']:.3f}%")

                st.markdown("**Pasos:**")
                for step in res_r['steps']:
                    st.markdown(f'<div class="gl-step">{step}</div>', unsafe_allow_html=True)

                # Comparison of all three methods
                st.markdown("**Comparación de métodos:**")
                col_l, col_m, col_r = st.columns(3)
                for col, meth, label in [
                    (col_l, 'left', 'Izquierda'),
                    (col_m, 'midpoint', 'Punto Medio'),
                    (col_r, 'right', 'Derecha'),
                ]:
                    res_m = riemann_sum(fr, ra, rb, nr, method=meth)
                    if not res_m.get('error'):
                        col.metric(
                            label,
                            f"{res_m['suma']:.5f}",
                            f"err {res_m['error_pct']:.2f}%",
                            delta_color="off"
                        )

                # Chart
                try:
                    import sympy as sp
                    from math_engine import parse_function
                    from charts import grafico_riemann
                    expr, err = parse_function(fr)
                    if not err:
                        f_l = sp.lambdify(sp.Symbol('x'), expr, 'numpy')
                        x_p = np.linspace(ra - 0.5, rb + 0.5, 500)
                        y_p = np.clip(np.array(f_l(x_p), dtype=float), -1e4, 1e4)
                        fig = grafico_riemann(x_p, y_p, ra, rb, nr, method=metodo_r)
                        st.plotly_chart(fig, width='stretch')
                except Exception as e:
                    st.error(f"Error al graficar: {e}")


def render_presupuesto(perdidas: PropagationLoss):
    st.markdown("#### 📻 Presupuesto del Enlace RF")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("FSPL", f"{perdidas.fspl_db:.2f} dB")
        st.metric("Pérdida difracción", f"{perdidas.perdida_difraccion_db:.2f} dB")
        st.metric("Pérdida total", f"{perdidas.perdida_total_db:.2f} dB")
    with c2:
        st.metric("Potencia RX", f"{perdidas.potencia_rx_dbm:.2f} dBm")
        st.metric("Margen del enlace", f"{perdidas.margen_enlace_db:.2f} dB",
                  delta="viable" if perdidas.viable else "no viable",
                  delta_color="normal" if perdidas.viable else "inverse")
        st.metric("RSSI estimado", perdidas.rssi_estimado)

    from charts import grafico_presupuesto_enlace
    st.plotly_chart(grafico_presupuesto_enlace(perdidas), width='stretch')


def render_analisis_sensibilidad(link: LinkParameters, obstaculos: list):
    from terrain_engine import analisis_sensibilidad_frecuencia, analisis_altura_optima
    from charts import grafico_sensibilidad_frecuencia, grafico_altura_optima
    import pandas as pd

    st.markdown("#### 🔬 Análisis de Sensibilidad")
    tab_f, tab_h = st.tabs(["📶 Por Frecuencia", "📏 Por Altura de Antena"])

    with tab_f:
        freqs = [round(f, 1) for f in np.arange(2.4, 6.2, 0.2).tolist()]
        with st.spinner("Calculando..."):
            res = analisis_sensibilidad_frecuencia(link, obstaculos, freqs)
        st.plotly_chart(grafico_sensibilidad_frecuencia(res), width='stretch')
        df = pd.DataFrame({
            "Frecuencia (GHz)": res['frecuencias'],
            "Radio Fresnel Máx. (m)": [f"{v:.2f}" for v in res['radio_fresnel_max']],
            "Área Obstrucción": [f"{v:.4f}" for v in res['area_obs']],
            "FSPL (dB)": [f"{v:.2f}" for v in res['fspl']],
            "Viable": ["✅" if v else "❌" for v in res['viable']],
        })
        st.dataframe(df, width='stretch', hide_index=True)

    with tab_h:
        ant = st.radio("Antena a analizar:", ["A (TX)", "B (RX)"], horizontal=True)
        key = "A" if "A" in ant else "B"
        alturas = list(range(5, 155, 5))
        with st.spinner("Calculando..."):
            res_h = analisis_altura_optima(link, obstaculos, alturas, antena=key)
        st.plotly_chart(grafico_altura_optima(res_h, key), width='stretch')
        for h, v in zip(res_h['alturas'], res_h['viable']):
            if v:
                st.success(f"Altura mínima viable para Antena {key}: **{h} m**")
                break
        else:
            st.error("No se encontró altura viable en el rango 5–150 m.")


def render_recomendaciones(recomendaciones: dict, viento: dict,
                            link, perdidas) -> None:
    score = recomendaciones['score']
    recs = recomendaciones['recomendaciones']

    # Viability score badge
    if score >= 80:
        color, label, emoji = "#1D8348", "Instalación Óptima", "✅"
    elif score >= 50:
        color, label, emoji = "#D97706", "Viable con Ajustes", "⚠️"
    else:
        color, label, emoji = "#C0392B", "No Recomendado", "❌"

    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:12px;'
        f'padding:20px 24px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">'
        f'<span style="font-size:1rem;font-weight:700;color:#111827">🎯 Puntuación de Viabilidad</span>'
        f'<span style="background:{color};color:#fff;padding:4px 14px;border-radius:20px;'
        f'font-size:0.8rem;font-weight:700">{emoji} {label}</span>'
        f'</div>'
        f'<div style="background:#F3F4F6;border-radius:8px;height:12px;overflow:hidden">'
        f'<div style="background:{color};height:100%;width:{score}%;border-radius:8px;'
        f'transition:width 0.5s"></div>'
        f'</div>'
        f'<div style="text-align:right;font-size:1.4rem;font-weight:700;color:{color};margin-top:4px">'
        f'{score}/100</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("#### 💡 Recomendaciones del Sistema")
    for rec in recs:
        tipo = rec['tipo']
        if tipo == 'success':
            st.success(f"**{rec['titulo']}**")
        elif tipo == 'error':
            st.error(f"**{rec['titulo']}**")
        else:
            st.warning(f"**{rec['titulo']}**")
        for d in rec['detalle']:
            st.markdown(f"&nbsp;&nbsp;&nbsp;→ {d}")

    # Wind load summary
    st.markdown("#### 🌬️ Carga Estructural de Viento")
    cw1, cw2, cw3 = st.columns(3)
    cw1.metric("Fuerza sobre torre", f"{viento['fuerza_kg']:.1f} kg",
               help="F = 0.5 × Cd × ρ × A × v²")
    cw2.metric("Momento en base", f"{viento['momento_nm']:.0f} N·m")
    cw3.metric("Vel. máx. segura", f"{viento['v_max_kmh']:.0f} km/h",
               delta="✓ Seguro" if viento['seguro'] else "✗ Riesgo",
               delta_color="normal" if viento['seguro'] else "inverse")
