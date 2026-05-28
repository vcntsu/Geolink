"""
charts.py — Gráficos Plotly con tema claro estilo AWS/SaaS
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from terrain_engine import TerrainProfile, LinkParameters, PropagationLoss

# AWS-inspired light palette
C = {
    'bg':        '#FFFFFF',
    'bg_plot':   '#F8F9FA',
    'grid':      '#E5E7EB',
    'zeroline':  '#D1D5DB',
    'text':      '#111827',
    'sub':       '#6B7280',
    'blue':      '#007AFF',
    'green':     '#27AE60',
    'red':       '#E74C3C',
    'orange':    '#FF9900',
    'yellow':    '#F59E0B',
    'purple':    '#8B5CF6',
    'cyan':      '#0891B2',
    'terrain':   '#27AE60',
    'terrain_f': 'rgba(39,174,96,0.15)',
    'fr1':       'rgba(245,158,11,0.08)',
    'fr1_b':     'rgba(245,158,11,0.55)',
    'fr06':      'rgba(0,122,255,0.08)',
    'fr06_b':    'rgba(0,122,255,0.65)',
    'obs':       'rgba(231,76,60,0.25)',
    'obs_b':     '#E74C3C',
    'ant':       '#8B5CF6',
}

_BASE = dict(
    paper_bgcolor=C['bg'],
    plot_bgcolor=C['bg_plot'],
    font=dict(color=C['text'], family='Inter, -apple-system, sans-serif', size=12),
    margin=dict(l=50, r=20, t=45, b=45),
    hovermode='x unified',
    legend=dict(
        orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
        bgcolor='rgba(255,255,255,0.95)', bordercolor='#E5E7EB', borderwidth=1,
        font=dict(size=11, color='#374151')
    ),
    xaxis=dict(
        gridcolor=C['grid'], zerolinecolor=C['zeroline'],
        tickfont=dict(color=C['sub']), title_font=dict(color=C['sub']),
        linecolor=C['grid'],
    ),
    yaxis=dict(
        gridcolor=C['grid'], zerolinecolor=C['zeroline'],
        tickfont=dict(color=C['sub']), title_font=dict(color=C['sub']),
        linecolor=C['grid'],
    ),
)


def _layout(**kwargs):
    d = dict(_BASE)
    d.update(kwargs)
    return d


def grafico_perfil_enlace(perfil: TerrainProfile, link: LinkParameters,
                           mostrar_r1=True, mostrar_r06=True, mostrar_curvatura=False):
    fig = go.Figure()
    x = perfil.x

    if mostrar_r1:
        fig.add_trace(go.Scatter(
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([perfil.fresnel_r1_superior, perfil.fresnel_r1_inferior[::-1]]),
            fill='toself', fillcolor=C['fr1'],
            line=dict(color=C['fr1_b'], width=1, dash='dot'),
            name='Fresnel R₁ (100%)', hoverinfo='skip'
        ))

    if mostrar_r06:
        fig.add_trace(go.Scatter(
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([perfil.fresnel_r06_superior, perfil.fresnel_r06_inferior[::-1]]),
            fill='toself', fillcolor=C['fr06'],
            line=dict(color=C['fr06_b'], width=1.5, dash='dash'),
            name='Fresnel R₀.₆ (60%) — Ubiquiti', hoverinfo='skip'
        ))

    if perfil.area_obstruccion > 0:
        y_top = np.where(perfil.obstruccion_mask, perfil.elevacion, perfil.fresnel_r06_inferior)
        fig.add_trace(go.Scatter(
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([y_top, perfil.fresnel_r06_inferior[::-1]]),
            fill='toself', fillcolor=C['obs'],
            line=dict(color=C['obs_b'], width=0),
            name=f'Área Obstruida  {perfil.area_obstruccion:.3f} m·km',
            hoverinfo='skip'
        ))

    fig.add_trace(go.Scatter(
        x=x, y=perfil.elevacion,
        name='Terreno', fill='tozeroy', fillcolor=C['terrain_f'],
        line=dict(color=C['terrain'], width=2.5),
        hovertemplate='<b>%{x:.2f} km</b> → %{y:.1f} m<extra>Terreno</extra>'
    ))

    fig.add_trace(go.Scatter(
        x=x, y=perfil.linea_vista,
        name='Línea de Vista (LoS)',
        line=dict(color=C['blue'], width=2.5, dash='dash'),
        hovertemplate='LoS: %{y:.1f} m<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=[0, link.distancia_km],
        y=[link.altura_antena_a, link.altura_antena_b],
        mode='markers+text',
        marker=dict(symbol='triangle-up', size=18, color=C['ant'],
                    line=dict(color='white', width=2)),
        text=['Antena A', 'Antena B'],
        textposition=['top right', 'top left'],
        textfont=dict(size=11, color=C['ant']),
        name='Antenas',
        hovertemplate='<b>%{text}</b>: %{y} m<extra></extra>'
    ))

    idx = int(np.argmin(perfil.fresnel_r06_inferior - perfil.elevacion))
    xc = float(x[idx])
    yc = (float(perfil.elevacion[idx]) + float(perfil.fresnel_r06_inferior[idx])) / 2
    if perfil.clearance_minimo < 0:
        fig.add_annotation(x=xc, y=yc,
            text=f"⚠️ -{abs(perfil.clearance_minimo):.1f} m",
            showarrow=True, arrowhead=2, arrowcolor=C['red'],
            font=dict(color=C['red'], size=11),
            bgcolor='rgba(231,76,60,0.1)', bordercolor=C['red'], borderwidth=1)
    else:
        fig.add_annotation(x=xc, y=yc,
            text=f"✓ +{perfil.clearance_minimo:.1f} m",
            showarrow=True, arrowhead=2, arrowcolor=C['green'],
            font=dict(color=C['green'], size=11),
            bgcolor='rgba(39,174,96,0.1)', bordercolor=C['green'], borderwidth=1)

    fig.update_layout(**_layout(
        xaxis=dict(**_BASE['xaxis'], title='Distancia (km)'),
        yaxis=dict(**_BASE['yaxis'], title='Elevación (m)'),
        title=dict(text='Perfil de Elevación del Enlace RF', font=dict(size=14, color=C['text']), x=0.5),
        height=420
    ))
    return fig


def grafico_derivada_terreno(x, terreno, d1, d2):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
        subplot_titles=("h(x) — Terreno", "h'(x) — Pendiente", "h''(x) — Concavidad"),
        vertical_spacing=0.07)

    fig.add_trace(go.Scatter(x=x, y=terreno, name='h(x)',
        fill='tozeroy', fillcolor=C['terrain_f'],
        line=dict(color=C['terrain'], width=2)), row=1, col=1)

    fig.add_trace(go.Scatter(x=x, y=d1, name="h'(x)",
        fill='tozeroy', fillcolor='rgba(255,153,0,0.12)',
        line=dict(color=C['orange'], width=2)), row=2, col=1)
    fig.add_hline(y=0, line=dict(color=C['zeroline'], width=1, dash='dot'), row=2, col=1)

    fig.add_trace(go.Scatter(x=x, y=d2, name="h''(x)",
        fill='tozeroy', fillcolor='rgba(139,92,246,0.12)',
        line=dict(color=C['purple'], width=2)), row=3, col=1)
    fig.add_hline(y=0, line=dict(color=C['zeroline'], width=1, dash='dot'), row=3, col=1)

    fig.update_layout(**_layout(height=480,
        title=dict(text='Análisis Diferencial del Terreno', font=dict(size=13, color=C['text']), x=0.5)))
    fig.update_xaxes(gridcolor=C['grid'], tickfont=dict(color=C['sub']), linecolor=C['grid'])
    fig.update_yaxes(gridcolor=C['grid'], tickfont=dict(color=C['sub']), linecolor=C['grid'])
    return fig


def grafico_radio_fresnel(x, link: LinkParameters):
    from terrain_engine import calcular_radio_fresnel
    fig = go.Figure()
    freqs = [2.4, 5.0, 5.8, 6.0]
    cols = [C['green'], C['blue'], C['orange'], C['red']]
    for f, col in zip(freqs, cols):
        lt = LinkParameters(link.distancia_km, f, link.altura_antena_a, link.altura_antena_b)
        r = calcular_radio_fresnel(x, lt)
        fig.add_trace(go.Scatter(x=x, y=r, name=f'{f} GHz',
            line=dict(color=col, width=2),
            hovertemplate=f'{f} GHz: %{{y:.1f}} m<extra></extra>'))
    fig.update_layout(**_layout(
        xaxis=dict(**_BASE['xaxis'], title='Distancia (km)'),
        yaxis=dict(**_BASE['yaxis'], title='Radio Fresnel (m)'),
        title=dict(text='Radio de Fresnel por Frecuencia', font=dict(size=13, color=C['text']), x=0.5),
        height=320
    ))
    return fig


def grafico_presupuesto_enlace(perdidas: PropagationLoss):
    cats = ['EIRP TX', 'FSPL', 'Difracción', 'Ganancia RX', 'Potencia RX', 'Sensibilidad']
    vals = [
        perdidas.fspl_db + perdidas.perdida_difraccion_db + perdidas.potencia_rx_dbm,
        -perdidas.fspl_db, -perdidas.perdida_difraccion_db, 0,
        perdidas.potencia_rx_dbm,
        perdidas.potencia_rx_dbm - perdidas.margen_enlace_db
    ]
    bar_cols = [C['green'], C['red'], C['orange'], C['blue'], C['purple'], C['sub']]
    fig = go.Figure(go.Bar(
        x=cats, y=[abs(v) for v in vals],
        marker_color=bar_cols,
        text=[f'{v:+.1f} dB' for v in vals],
        textposition='outside',
        textfont=dict(color=C['text'], size=11)
    ))
    fig.update_layout(**_layout(
        yaxis=dict(**_BASE['yaxis'], title='dB'),
        title=dict(text='Presupuesto del Enlace', font=dict(size=13, color=C['text']), x=0.5),
        height=320
    ))
    return fig


def grafico_sensibilidad_frecuencia(res: dict):
    fig = make_subplots(rows=1, cols=2,
        subplot_titles=('Radio Fresnel Máx. vs Frecuencia', 'FSPL vs Frecuencia'),
        horizontal_spacing=0.12)

    marker_cols = [C['green'] if v else C['red'] for v in res['viable']]
    fig.add_trace(go.Scatter(
        x=res['frecuencias'], y=res['radio_fresnel_max'],
        mode='lines+markers', name='Radio Fresnel',
        line=dict(color=C['yellow'], width=2),
        marker=dict(size=8, color=marker_cols)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=res['frecuencias'], y=res['fspl'],
        mode='lines+markers', name='FSPL (dB)',
        line=dict(color=C['blue'], width=2),
        marker=dict(size=8, color=C['blue'])
    ), row=1, col=2)

    fig.update_layout(**_layout(height=340,
        title=dict(text='Sensibilidad por Frecuencia', font=dict(size=13, color=C['text']), x=0.5)))
    fig.update_xaxes(title_text='Frecuencia (GHz)', gridcolor=C['grid'], tickfont=dict(color=C['sub']))
    fig.update_yaxes(gridcolor=C['grid'], tickfont=dict(color=C['sub']))
    return fig


def grafico_altura_optima(res: dict, antena: str):
    fig = go.Figure()
    cols = [C['green'] if v else C['red'] for v in res['viable']]
    fig.add_trace(go.Scatter(
        x=res['alturas'], y=res['clearance'],
        mode='lines+markers', name='Clearance mínimo',
        line=dict(color=C['cyan'], width=2.5),
        marker=dict(size=9, color=cols, line=dict(color='white', width=1))
    ))
    fig.add_hline(y=0, line=dict(color=C['red'], width=2, dash='dash'),
                  annotation_text='Límite viable', annotation_font_color=C['red'])
    fig.update_layout(**_layout(
        xaxis=dict(**_BASE['xaxis'], title=f'Altura Antena {antena} (m)'),
        yaxis=dict(**_BASE['yaxis'], title='Clearance mínimo (m)'),
        title=dict(text=f'Altura Óptima — Antena {antena}', font=dict(size=13, color=C['text']), x=0.5),
        height=320
    ))
    return fig


def grafico_funcion_personalizada(x_vals, y_vals, dy_vals, iy_vals, func_str):
    fig = make_subplots(rows=1, cols=3,
        subplot_titles=('f(x)', "f'(x) Derivada", '∫f(x)dx Integral'),
        horizontal_spacing=0.08)

    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, name='f(x)',
        line=dict(color=C['green'], width=2.5),
        fill='tozeroy', fillcolor='rgba(39,174,96,0.1)'), row=1, col=1)

    fig.add_trace(go.Scatter(x=x_vals, y=dy_vals, name="f'(x)",
        line=dict(color=C['orange'], width=2.5),
        fill='tozeroy', fillcolor='rgba(255,153,0,0.1)'), row=1, col=2)
    fig.add_hline(y=0, line=dict(color=C['zeroline'], width=1, dash='dot'), row=1, col=2)

    fig.add_trace(go.Scatter(x=x_vals, y=iy_vals, name='∫f(x)dx',
        line=dict(color=C['purple'], width=2.5),
        fill='tozeroy', fillcolor='rgba(139,92,246,0.1)'), row=1, col=3)

    fig.update_layout(**_layout(height=340,
        title=dict(text=f'Análisis de f(x) = {func_str}', font=dict(size=13, color=C['text']), x=0.5)))
    fig.update_xaxes(gridcolor=C['grid'], tickfont=dict(color=C['sub']))
    fig.update_yaxes(gridcolor=C['grid'], tickfont=dict(color=C['sub']))
    return fig


def grafico_riemann(x_vals, y_vals, a, b, n_rect=20, method='midpoint'):
    """Riemann sum chart supporting left, right, and midpoint methods."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals, name='f(x)',
        line=dict(color=C['blue'], width=2.5)
    ))

    dx_r = (b - a) / n_rect
    x_rect = np.linspace(a, b, n_rect + 1)

    for i in range(n_rect):
        if method == 'left':
            xi_eval = x_rect[i]
        elif method == 'right':
            xi_eval = x_rect[i + 1]
        else:  # midpoint
            xi_eval = x_rect[i] + dx_r / 2

        yi = float(np.interp(xi_eval, x_vals, y_vals))
        fc = 'rgba(0,122,255,0.25)' if yi >= 0 else 'rgba(231,76,60,0.25)'
        bc = C['blue'] if yi >= 0 else C['red']
        fig.add_shape(type='rect', x0=x_rect[i], x1=x_rect[i] + dx_r, y0=0, y1=yi,
                      fillcolor=fc, line=dict(color=bc, width=0.8))

    fig.add_vline(x=a, line=dict(color=C['orange'], width=2, dash='dash'),
                  annotation_text=f'a={a:.2f}', annotation_font_color=C['orange'])
    fig.add_vline(x=b, line=dict(color=C['orange'], width=2, dash='dash'),
                  annotation_text=f'b={b:.2f}', annotation_font_color=C['orange'])

    method_label = {'left': 'Izquierda', 'right': 'Derecha', 'midpoint': 'Punto Medio'}.get(method, method)
    fig.update_layout(**_layout(
        xaxis=dict(**_BASE['xaxis'], title='x'),
        yaxis=dict(**_BASE['yaxis'], title='f(x)'),
        title=dict(
            text=f'Suma de Riemann ({method_label}) — {n_rect} rect. en [{a:.2f}, {b:.2f}]',
            font=dict(size=13, color=C['text']), x=0.5
        ),
        height=360
    ))
    return fig
