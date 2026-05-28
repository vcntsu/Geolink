"""
styles.py — AWS-inspired professional light theme for GeoLink Calc v2.1
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --aws-navy:   #232F3E;
    --aws-orange: #FF9900;
    --aws-blue:   #007AFF;
    --aws-green:  #1D8348;
    --aws-red:    #C0392B;
    --aws-purple: #8B5CF6;
    --bg-main:    #FFFFFF;
    --bg-section: #F8F9FA;
    --bg-card:    #FFFFFF;
    --border:     #E5E7EB;
    --text-title: #111827;
    --text-body:  #374151;
    --text-muted: #6B7280;
    --radius:     12px;
    --radius-sm:  8px;
    --shadow:     0 2px 8px rgba(0,0,0,0.08);
    --shadow-hover: 0 6px 20px rgba(0,0,0,0.13);
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, system-ui, sans-serif !important;
    background: var(--bg-main) !important;
    color: var(--text-body) !important;
    -webkit-font-smoothing: antialiased;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"],
.stDeployButton, [data-testid="stDeployButton"] {
    visibility: hidden !important;
    display: none !important;
}

/* ── Main container ── */
.block-container {
    padding: 0 2rem 4rem !important;
    max-width: 100% !important;
    background: var(--bg-main) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-section); }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 3px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.75rem 1rem !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-title) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
}
/* Slider thumb */
section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--aws-blue) !important;
    border: 2px solid #FFFFFF !important;
    box-shadow: 0 0 0 3px rgba(0,122,255,0.2) !important;
}
/* Slider track fill */
section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [data-testid="stSliderTrack"] > div:first-child {
    background: var(--aws-blue) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-section) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    padding: 7px 16px !important;
    border: none !important;
    transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
    background: var(--aws-orange) !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(255,153,0,0.35) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #FFFFFF !important;
    border: 1px solid #D1D5DB !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-title) !important;
    font-size: 0.88rem !important;
    padding: 9px 13px !important;
}
.stTextInput > div > div > input::placeholder,
.stNumberInput > div > div > input::placeholder {
    color: #9CA3AF !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--aws-blue) !important;
    box-shadow: 0 0 0 3px rgba(0,122,255,0.12) !important;
    outline: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--aws-blue) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    padding: 10px 22px !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 4px rgba(0,122,255,0.25) !important;
}
.stButton > button:hover {
    background: #0066DD !important;
    box-shadow: 0 4px 14px rgba(0,122,255,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #FFFFFF !important;
    border: 1px solid #D1D5DB !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-title) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: var(--radius-sm) !important;
    padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.73rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-title) !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; font-weight: 600 !important; }

/* ── Alerts ── */
.stSuccess {
    background: #F0FDF4 !important;
    border-left: 4px solid var(--aws-green) !important;
    border-radius: var(--radius-sm) !important;
    color: #14532D !important;
}
.stError {
    background: #FEF2F2 !important;
    border-left: 4px solid var(--aws-red) !important;
    border-radius: var(--radius-sm) !important;
    color: #7F1D1D !important;
}
.stInfo {
    background: #EFF6FF !important;
    border-left: 4px solid var(--aws-blue) !important;
    border-radius: var(--radius-sm) !important;
    color: #1E3A5F !important;
}
.stWarning {
    background: #FFFBEB !important;
    border-left: 4px solid var(--aws-orange) !important;
    border-radius: var(--radius-sm) !important;
    color: #78350F !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--bg-section) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-body) !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

/* ── Code ── */
code {
    background: #EFF6FF !important;
    color: #1D4ED8 !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
    font-size: 0.82em !important;
}

/* ══ CUSTOM COMPONENTS ══ */

/* Header bar */
.gl-header {
    background: var(--aws-navy);
    padding: 22px 38px 20px;
    margin: 0 -2rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}
.gl-header-left { display: flex; align-items: center; gap: 14px; }
.gl-logo {
    font-size: 1.75rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.5px;
    line-height: 1;
}
.gl-logo span { color: var(--aws-orange); }
.gl-tagline {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.6);
    line-height: 1.5;
    max-width: 420px;
}
.gl-badges { display: flex; gap: 7px; flex-wrap: wrap; }
.gl-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 11px;
    border-radius: 20px;
    font-size: 0.71rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.b-orange { background: rgba(255,153,0,0.18); color: #FF9900; border: 1px solid rgba(255,153,0,0.35); }
.b-blue   { background: rgba(0,122,255,0.15);  color: #60A5FA; border: 1px solid rgba(0,122,255,0.3); }
.b-green  { background: rgba(29,131,72,0.15);  color: #34D399; border: 1px solid rgba(29,131,72,0.3); }
.b-purple { background: rgba(139,92,246,0.15); color: #A78BFA; border: 1px solid rgba(139,92,246,0.3); }

/* Sub-nav pill bar */
.gl-subnav {
    background: #FFFFFF;
    border-bottom: 1px solid var(--border);
    padding: 10px 38px;
    margin: 0 -2rem 24px;
    display: flex;
    gap: 6px;
}

/* KPI row */
.gl-kpi-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.gl-kpi {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 14px;
    text-align: left;
    transition: all 0.18s;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow);
}
.gl-kpi::before {
    content: '';
    position: absolute; top: 0; left: 0; bottom: 0;
    width: 4px;
    border-radius: var(--radius) 0 0 var(--radius);
}
.kc-blue::before   { background: #007AFF; }
.kc-green::before  { background: #1D8348; }
.kc-red::before    { background: #C0392B; }
.kc-orange::before { background: #FF9900; }
.kc-purple::before { background: #8B5CF6; }
.kc-cyan::before   { background: #0891B2; }
.gl-kpi:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
.gl-kv {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--text-title);
    line-height: 1.2;
    margin-bottom: 4px;
    padding-left: 10px;
}
.gl-kl {
    font-size: 0.67rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    padding-left: 10px;
}

/* Status banners */
.gl-status {
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}
.gl-ok  { background: #FFFFFF; border-left: 4px solid #1D8348; }
.gl-err { background: #FFFFFF; border-left: 4px solid #C0392B; }
.gl-si  { font-size: 1.4rem; flex-shrink: 0; margin-top: 1px; }
.gl-st  { font-size: 0.95rem; font-weight: 700; margin-bottom: 3px; color: var(--text-title); }
.gl-sd  { font-size: 0.82rem; color: var(--text-body); line-height: 1.6; }

/* Math step cards */
.gl-step {
    background: #F0F7FF;
    border: 1px solid #BFDBFE;
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    margin: 5px 0;
    font-size: 0.84rem;
    line-height: 1.7;
    color: var(--text-body);
}

/* Section divider */
.gl-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0 20px;
}

/* Dot pulse */
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.gl-dot {
    display: inline-block; width: 7px; height: 7px;
    background: #1D8348; border-radius: 50%;
    margin-right: 5px; animation: pulse 2s infinite;
}

@media (max-width: 900px) { .gl-kpi-row { grid-template-columns: repeat(3,1fr); } }
@media (max-width: 600px) { .gl-kpi-row { grid-template-columns: repeat(2,1fr); } }
</style>
"""


def render_header() -> str:
    return """
<div class="gl-header">
  <div class="gl-header-left">
    <div>
      <div class="gl-logo">📡 GeoLink<span>Calc</span></div>
      <div class="gl-tagline">
        Simulador de enlaces RF · Zona de Fresnel · Cálculo Simbólico SymPy · Gráficos Plotly
      </div>
    </div>
  </div>
  <div class="gl-badges">
    <span class="gl-badge b-orange"><span class="gl-dot"></span>Tiempo Real</span>
    <span class="gl-badge b-blue">📐 Cálculo Simbólico</span>
    <span class="gl-badge b-green">🗺️ Perfil de Terreno</span>
    <span class="gl-badge b-purple">📊 Zona de Fresnel</span>
  </div>
</div>"""


def render_kpi_row(items: list) -> str:
    cards = ""
    for val, lbl, color in items:
        cards += (
            f'<div class="gl-kpi kc-{color}">'
            f'<div class="gl-kv">{val}</div>'
            f'<div class="gl-kl">{lbl}</div>'
            f'</div>'
        )
    return f'<div class="gl-kpi-row">{cards}</div>'


def render_status(viable: bool, area_obs: float, clearance: float, margen_db: float) -> str:
    if viable:
        return f"""
<div class="gl-status gl-ok">
  <div class="gl-si">✅</div>
  <div>
    <div class="gl-st" style="color:#1D8348">ENLACE VIABLE — Zona de Fresnel Despejada</div>
    <div class="gl-sd">
      El terreno no penetra el 60% de la primera zona de Fresnel. &nbsp;
      Clearance mínimo: <strong>{clearance:.1f} m</strong> &nbsp;·&nbsp;
      Área de obstrucción: <strong>0.000 m²</strong> &nbsp;·&nbsp;
      Margen estimado: <strong>+{margen_db:.1f} dB</strong>
    </div>
  </div>
</div>"""
    else:
        return f"""
<div class="gl-status gl-err">
  <div class="gl-si">❌</div>
  <div>
    <div class="gl-st" style="color:#C0392B">ENLACE NO VIABLE — Obstrucción Detectada</div>
    <div class="gl-sd">
      El terreno penetra la zona de Fresnel. Se producirán pérdidas por difracción. &nbsp;
      Área de obstrucción: <strong>{area_obs:.2f} m²</strong> &nbsp;·&nbsp;
      Penetración: <strong>{abs(clearance):.1f} m</strong> &nbsp;·&nbsp;
      Acción: aumentar altura de antenas o cambiar frecuencia.
    </div>
  </div>
</div>"""
