import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de la página web estilo Dashboard moderno
st.set_page_config(layout="wide", page_title="GeoLink Calc", page_icon="📡")

st.title("📡 GeoLink Calc: Simulador de Enlaces y Calculadora de Cálculo Integral")
st.markdown("""
Esta herramienta fusiona un simulador de radiofrecuencia (estilo *Radio Mobile*) con un motor de cálculo diferencial e integral 
para evaluar la viabilidad de instalación de antenas Ubiquiti.
""")

st.sidebar.header("⚙️ Parámetros del Enlace")

# Controles deslizantes para los datos técnicos
distancia_total = st.sidebar.slider("Distancia del enlace (Km)", 1.0, 50.0, 20.0, 0.5)
frecuencia = st.sidebar.slider("Frecuencia de operación (GHz)", 2.4, 6.0, 5.0, 0.1)
altura_antena_a = st.sidebar.slider("Altura Antena A (Transmisor) (m)", 10, 100, 40)
altura_antena_b = st.sidebar.slider("Altura Antena B (Receptor) (m)", 10, 100, 35)

st.sidebar.header("⛰️ Modelado del Terreno (Obstáculo)")
altura_cerro = st.sidebar.slider("Altura máxima del cerro (m)", 0, 120, 45)
posicion_cerro = st.sidebar.slider("Posición del cerro (Km)", 1.0, distancia_total - 1.0, distancia_total / 2, 0.5)
ancho_cerro = st.sidebar.slider("Ancho o extensión del cerro", 1.0, 10.0, 4.0, 0.5)

# --- MOTOR MATEMÁTICO (CÁLCULO Y ARITMÉTICA) ---

# Creación del vector de distancia (Eje X) - 500 puntos para suavidad tipo GeoGebra
x = np.linspace(0, distancia_total, 500)
dx = x[1] - x[0]  # Diferencial de x para la integración

# 1. Función de la Línea de Vista (LoS) - Ecuación de la recta
linea_vista = altura_antena_a + ((altura_antena_b - altura_antena_a) / distancia_total) * x

# 2. Función del Radio de la Zona de Fresnel (Elipsoide)
# Fórmula estándar: r = 17.32 * sqrt((d1 * d2) / (f * D))
d1 = x
d2 = distancia_total - x
fresnel_radius = 17.32 * np.sqrt((d1 * d2) / (frecuencia * distancia_total))

# Límites de la zona de Fresnel
fresnel_superior = linea_vista + fresnel_radius
fresnel_inferior = linea_vista - fresnel_radius

# 3. Función del Terreno (Modelado como una campana de Gauss)
terreno = altura_cerro * np.exp(-((x - posicion_cerro) / (ancho_cerro / 2))**2)

# --- APLICACIÓN DEL CÁLCULO INTEGRAL Y DIFERENCIAL ---

# A. DERIVADA: Pendiente del terreno (dh/dx) usando diferencias centrales
derivada_terreno = np.gradient(terreno, dx)
# Encontrar el punto máximo donde la derivada es cercana a cero (Criterio de la 1° derivada)
indice_max_pendiente = np.argmax(terreno)
punto_critico_x = x[indice_max_pendiente]

# B. INTEGRAL DEFINIDA: Área de obstrucción dentro de la zona de Fresnel inferior
# La obstrucción ocurre únicamente donde el terreno es mayor que el límite inferior de Fresnel
obstruccion_y = np.maximum(0, terreno - fresnel_inferior)
# Integral definida usando la regla del trapecio (Suma de Riemann acumulada)
area_obstruccion_total = np.trapz(obstruccion_y, x)

# Determinación de viabilidad
viable = area_obstruccion_total == 0

# --- DISEÑO DE LA INTERFAZ DE PANTALLA DIVIDIDA ---

col_grafico, col_calculos = st.columns([2, 1])

with col_grafico:
    st.subheader("🗺️ Perfil de Elevación del Enlace (Estilo Radio Mobile)")
    
    # Crear gráfico interactivo con Plotly
    fig = go.Figure()
    
    # Dibujar el Terreno
    fig.add_trace(go.Scatter(x=x, y=terreno, name="Terreno (Cerro)", fill='tozeroy', line=dict(color='green', width=2)))
    
    # Dibujar la Línea de Vista (LoS)
    fig.add_trace(go.Scatter(x=x, y=linea_vista, name="Línea de Vista (LoS)", line=dict(color='blue', width=2, dash='dash')))
    
    # Dibujar Zona de Fresnel Inferior (Límite crítico)
    fig.add_trace(go.Scatter(x=x, y=fresnel_inferior, name="Zona Fresnel Inferior (60%)", line=dict(color='orange', width=1.5, dash='dot')))
    
    # Sombrear el área de la INTEGRAL (Zona de obstrucción roja)
    if not viable:
        fig.add_trace(go.Scatter(
            x=x, y=np.where(obstruccion_y > 0, terreno, fresnel_inferior),
            fill='tonexty', fillcolor='rgba(255, 0, 0, 0.3)',
            line=dict(color='rgba(255,0,0,0)'), name="Área Obstruida (Integral)"
        ))

    # Configuración de etiquetas estilo ejes cartesianos de GeoGebra
    fig.update_layout(
        xaxis_title="Distancia (Km)",
        yaxis_title="Altura / Elevación (m)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertas dinámicas de viabilidad
    if viable:
        st.success("✅ ¡ENLACE VIABLE! La Zona de Fresnel está completamente despejada de obstáculos.")
    else:
        st.error(f"❌ ENLACE NO VIABLE. Existe una obstrucción geométrica detectada por el cálculo de la integral.")

with col_calculos:
    st.subheader("🧮 Panel de Control Matemático")
    
    st.markdown("### 🛠️ Aplicación de la Derivada")
    st.write("Calculando la razón de cambio instantánea del terreno $\\frac{dh}{dx}$:")
    st.metric(label="Punto Crítico del Terreno (Máximo)", value=f"{punto_critico_x:.2f} Km")
    st.caption("La primera derivada se iguala a 0 en este punto para localizar la cumbre exacta del obstáculo.")
    
    st.markdown("---")
    
    st.markdown("### 📐 Aplicación de la Integral Definida")
    st.write("Área bajo la curva del terreno que invade el elipsoide:")
    st.metric(label="Área de Interferencia Acumulada", value=f"{area_obstruccion_total:.3f} m·Km", delta=f"{area_obstruccion_total:.1f} unidades" if not viable else None, delta_color="inverse")
    
    st.info("""
    **Fórmula aplicada en el backend:**
    $$Área = \int_{0}^{D} \max(0, h(x) - f_{inferior}(x)) \, dx$$
    Donde la integral acumula infinitesimalmente el espacio donde el terreno rompe la línea de resguardo de Ubiquiti.
    """)