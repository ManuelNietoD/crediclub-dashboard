import streamlit as st
from pathlib import Path

# ── Page config (must be first) ─────────────────────────────────────────────
st.set_page_config(
    page_title="CrediClub · Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.theme import CARD_CSS, PRIMARY, TEXT_MUTED, BG_DARK
from utils.data_loader import load_data, load_empleados_raw
from pills import general, geografica, sucursales

# ── Inject global CSS ────────────────────────────────────────────────────────
st.markdown(CARD_CSS, unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
logo_path = Path(__file__).parent / "assets" / "logo.jpg"

col_logo, col_title, col_spacer = st.columns([1, 6, 1])
with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=72)
with col_title:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;height:72px;gap:12px">
          <div>
            <div style="font-size:22px;font-weight:700;color:#f0f0f0;line-height:1.1">
              Dashboard de Crédito
            </div>
            <div style="font-size:12px;color:{TEXT_MUTED};letter-spacing:0.08em;text-transform:uppercase">
              Analítica operativa · CrediClub
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(f'<hr style="border:none;border-top:1px solid rgba(0,196,204,0.2);margin:4px 0 18px 0">', unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Cargando datos…"):
    df = load_data()
    emp_raw = load_empleados_raw()

# ── Date range info ──────────────────────────────────────────────────────────
fecha_min = df["fecha_inicio"].min().strftime("%d %b %Y")
fecha_max = df["fecha_inicio"].max().strftime("%d %b %Y")
st.markdown(
    f'<div style="font-size:11px;color:{TEXT_MUTED};margin-bottom:16px">'
    f'📅 Período: <b style="color:#aaa">{fecha_min}</b> — <b style="color:#aaa">{fecha_max}</b>'
    f' &nbsp;|&nbsp; <b style="color:{PRIMARY}">{len(df):,}</b> créditos totales'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Pills navigation ─────────────────────────────────────────────────────────
pill = st.pills(
    label="",
    options=["📊 General", "🗺️ Geográfica", "🏢 Sucursales & Empleados"],
    default="📊 General",
    key="main_pill",
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Render pill ──────────────────────────────────────────────────────────────
if pill == "📊 General":
    general.render(df)
elif pill == "🗺️ Geográfica":
    geografica.render(df)
elif pill == "🏢 Sucursales & Empleados":
    sucursales.render(df, emp_raw)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="margin-top:48px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);'
    f'font-size:10px;color:{TEXT_MUTED};text-align:center">'
    f'CrediClub · Dashboard Analítico · Datos al {fecha_max}'
    f'</div>',
    unsafe_allow_html=True,
)
