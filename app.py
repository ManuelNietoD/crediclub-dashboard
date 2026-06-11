import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="CrediClub · Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.theme import CARD_CSS, PRIMARY, TEXT_MUTED
from utils.data_loader import load_data, load_empleados_raw
from pills import general, geografica, sucursales

st.markdown(CARD_CSS, unsafe_allow_html=True)

# ── Extra CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* hide sidebar toggle & default padding */
  [data-testid="collapsedControl"] { display: none; }
  section[data-testid="stSidebar"] { display: none; }
  .block-container { padding-top: 1.2rem !important; max-width: 100% !important; }

  /* pill nav */
  .nav-pills {
    display: flex;
    justify-content: center;
    gap: 10px;
    padding: 10px 0 18px 0;
  }
  .nav-pill {
    flex: 1;
    max-width: 320px;
    text-align: center;
    padding: 10px 0;
    border-radius: 99px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid rgba(0,196,204,0.3);
    color: #888;
    background: rgba(0,196,204,0.04);
    user-select: none;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
  }
  .nav-pill.active {
    background: rgba(0,196,204,0.15);
    border-color: #00c4cc;
    color: #00c4cc;
  }
  .nav-pill:hover:not(.active) {
    border-color: rgba(0,196,204,0.5);
    color: #ccc;
    background: rgba(0,196,204,0.07);
  }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Cargando datos…"):
    df = load_data()
    emp_raw = load_empleados_raw()

fecha_min = df["fecha_inicio"].min().strftime("%d %b %Y")
fecha_max = df["fecha_inicio"].max().strftime("%d %b %Y")

# ── Header ───────────────────────────────────────────────────────────────────
logo_path = Path(__file__).parent / "assets" / "logo.jpg"

col_logo, col_info, col_meta = st.columns([1, 5, 3])

with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=80)

with col_info:
    st.markdown(
        f"""
        <div style="padding:6px 0">
          <div style="font-size:22px;font-weight:700;color:#f0f0f0;line-height:1.2">
            Dashboard de Crédito
          </div>
          <div style="font-size:11px;color:{TEXT_MUTED};text-transform:uppercase;
                      letter-spacing:0.1em;margin-top:4px">
            Analítica Operativa · CrediClub
          </div>
          <div style="font-size:13px;color:#aaaaaa;margin-top:3px">
            Alejandro Manuel Nieto Delgado
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_meta:
    st.markdown(
        f"""
        <div style="text-align:right;padding:6px 0;line-height:2">
          <div style="font-size:12px;color:{TEXT_MUTED}">
            📅 <b style="color:#aaa">{fecha_min}</b> — <b style="color:#aaa">{fecha_max}</b>
          </div>
          <div style="font-size:12px;color:{TEXT_MUTED}">
            Créditos totales:&nbsp;
            <span style="color:#00c4cc;font-weight:700;font-size:15px">{len(df):,}</span>
          </div>
          <div style="font-size:12px;color:{TEXT_MUTED}">
            Cartera:&nbsp;
            <span style="color:#00c4cc;font-weight:700;font-size:15px">
              ${df["monto_pendiente"].sum()/1_000_000:.1f}M
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<hr style="border:none;border-top:1px solid rgba(0,196,204,0.2);margin:6px 0 0 0">',
    unsafe_allow_html=True,
)

# ── Pills navigation ─────────────────────────────────────────────────────────
pill = st.pills(
    label="",
    options=["📊  General", "🗺️  Geográfica", "🏢  Sucursales & Empleados"],
    default="📊  General",
    key="main_pill",
)

# Override pill styling to be full-width and centered
st.markdown("""
<style>
  div[data-testid="stPills"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
  }
  div[data-testid="stPills"] > div {
    display: flex !important;
    gap: 10px !important;
    width: 100% !important;
    justify-content: center !important;
  }
  div[data-testid="stPills"] button {
    flex: 1 !important;
    max-width: 340px !important;
    border-radius: 99px !important;
    padding: 10px 0 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    justify-content: center !important;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)

# ── Render ───────────────────────────────────────────────────────────────────
if pill == "📊  General":
    general.render(df)
elif pill == "🗺️  Geográfica":
    geografica.render(df)
elif pill == "🏢  Sucursales & Empleados":
    sucursales.render(df, emp_raw)

st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="margin-top:40px;padding-top:14px;'
    f'border-top:1px solid rgba(255,255,255,0.06);'
    f'font-size:10px;color:{TEXT_MUTED};text-align:center">'
    f'CrediClub · Dashboard Analítico · Alejandro Manuel Nieto Delgado · {fecha_max}'
    f'</div>',
    unsafe_allow_html=True,
)
