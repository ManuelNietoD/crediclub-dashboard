PRIMARY     = "#00c4cc"
PRIMARY_20  = "rgba(0,196,204,0.18)"
PRIMARY_40  = "rgba(0,196,204,0.40)"
BG_DARK     = "#0d0d0d"
BG_CARD     = "rgba(255,255,255,0.04)"
BORDER      = "rgba(0,196,204,0.25)"
TEXT_MAIN   = "#f0f0f0"
TEXT_MUTED  = "#888888"
WHITE       = "#ffffff"

# ── Paleta de 30 colores distinguibles para gráficas con muchos elementos ──
# Agrupa tonos: turquesas, azules, verdes, violetas, naranjas, rosas — todos
# con suficiente contraste sobre fondo oscuro pero sin saturación excesiva.
PALETTE_30 = [
    # turquesas / cyans
    "#00c4cc", "#00e0d0", "#00b3d9", "#00d9b3", "#00c4a0",
    # azules
    "#4da6ff", "#3385e0", "#1a66cc", "#6699ff", "#80b3ff",
    # verdes
    "#66cc88", "#44bb66", "#33aa55", "#88dd99", "#55cc77",
    # violetas / morados
    "#aa88ff", "#8866dd", "#cc99ff", "#9966cc", "#bb77ee",
    # naranjas / ámbar
    "#ffaa44", "#ff8833", "#ffbb66", "#dd9933", "#ffcc77",
    # rosas / corales
    "#ff7799", "#ee5577", "#ff99aa", "#dd6688", "#ffaabb",
]

# Subpaletas semánticas (para cuando todos los elementos son del mismo tipo)
PALETTE_SUCURSALES  = PALETTE_30          # hasta 30 sucursales
PALETTE_DIRECCIONES = [                   # 7 direcciones — colores bien distintos
    "#00c4cc", "#4da6ff", "#66cc88",
    "#aa88ff", "#ffaa44", "#ff7799", "#33aa55",
]
PALETTE_REGIONES = [                      # hasta 20 regiones
    "#00c4cc","#4da6ff","#66cc88","#aa88ff","#ffaa44",
    "#ff7799","#00e0d0","#3385e0","#44bb66","#8866dd",
    "#ff8833","#ee5577","#00b3d9","#1a66cc","#33aa55",
    "#9966cc","#dd9933","#dd6688","#80b3ff","#88dd99",
]

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_MAIN, family="Inter, sans-serif", size=12),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(color=TEXT_MUTED, size=11),
    ),
    margin=dict(l=16, r=16, t=40, b=16),
    hoverlabel=dict(
        bgcolor="#1a1a1a",
        bordercolor=PRIMARY,
        font=dict(color=WHITE, size=12),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color=TEXT_MUTED),
        title_font=dict(color=TEXT_MUTED),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color=TEXT_MUTED),
        title_font=dict(color=TEXT_MUTED),
    ),
)


def apply_theme(fig, title: str = ""):
    fig.update_layout(**BASE_LAYOUT, title=dict(
        text=title, font=dict(color=TEXT_MAIN, size=15), x=0.01, xanchor="left"
    ))
    return fig


CARD_CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Inter', sans-serif;
      background-color: {BG_DARK};
      color: {TEXT_MAIN};
  }}

  #MainMenu, footer, header {{ visibility: hidden; }}

  .kpi-card {{
      background: {BG_CARD};
      border: 1px solid {BORDER};
      border-radius: 14px;
      padding: 20px 24px;
      backdrop-filter: blur(8px);
      text-align: center;
  }}
  .kpi-label {{
      font-size: 12px;
      color: {TEXT_MUTED};
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
  }}
  .kpi-value {{
      font-size: 28px;
      font-weight: 700;
      color: {PRIMARY};
      line-height: 1.1;
  }}
  .kpi-sub {{
      font-size: 11px;
      color: {TEXT_MUTED};
      margin-top: 4px;
  }}

  .section-title {{
      font-size: 13px;
      font-weight: 600;
      color: {TEXT_MUTED};
      text-transform: uppercase;
      letter-spacing: 0.1em;
      border-left: 3px solid {PRIMARY};
      padding-left: 10px;
      margin: 24px 0 12px 0;
  }}

  [data-testid="stSidebar"] {{
      background-color: #0a0a0a;
      border-right: 1px solid {BORDER};
  }}
</style>
"""


def fmt_currency(val: float) -> str:
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.2f}B"
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:,.0f}"


def fmt_number(val: float) -> str:
    if val >= 1_000_000:
        return f"{val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"{val/1_000:.1f}K"
    return f"{val:,.0f}"


def kpi_card(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>"""


def section_title(text: str) -> str:
    return f'<div class="section-title">{text}</div>'
