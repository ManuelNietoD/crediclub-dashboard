import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="CrediClub · Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import CARD_CSS, PRIMARY, TEXT_MUTED, BG_DARK
from utils.data_loader import load_data, load_empleados_raw
from pills import general, geografica, sucursales

st.markdown(CARD_CSS, unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
logo_path = Path(__file__).parent / "assets" / "logo.jpg"

col_logo, col_title = st.columns([1, 9])
with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=110)
with col_title:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;height:110px">
          <div>
            <div style="font-size:26px;font-weight:700;color:#f0f0f0;line-height:1.2">
              Dashboard de Crédito
            </div>
            <div style="font-size:12px;color:{TEXT_MUTED};letter-spacing:0.08em;
                        text-transform:uppercase;margin-top:4px">
              Analítica Operativa · CrediClub
            </div>
            <div style="font-size:13px;color:#aaaaaa;margin-top:3px;font-weight:500">
              Alejandro Manuel Nieto Delgado
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f'<hr style="border:none;border-top:1px solid rgba(0,196,204,0.2);margin:4px 0 0 0">',
    unsafe_allow_html=True,
)

# ── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Cargando datos…"):
    df = load_data()
    emp_raw = load_empleados_raw()

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    if logo_path.exists():
        st.image(str(logo_path), width=80)

    st.markdown(
        f"""
        <div style="margin:8px 0 20px 0">
          <div style="font-size:15px;font-weight:700;color:#f0f0f0">CrediClub</div>
          <div style="font-size:10px;color:{TEXT_MUTED};text-transform:uppercase;
                      letter-spacing:0.08em">Dashboard Analítico</div>
        </div>
        <hr style="border:none;border-top:1px solid rgba(0,196,204,0.2);margin:0 0 16px 0">
        """,
        unsafe_allow_html=True,
    )

    pill = st.radio(
        "Navegación",
        options=["📊 General", "🗺️ Geográfica", "🏢 Sucursales & Empleados"],
        label_visibility="collapsed",
    )

    st.markdown(
        f"""
        <hr style="border:none;border-top:1px solid rgba(0,196,204,0.2);margin:20px 0 12px 0">
        <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.7">
          📅 <b style="color:#aaa">Período</b><br>
          11 oct 2025 — 31 ene 2026<br><br>
          📁 <b style="color:#aaa">Créditos totales</b><br>
          <span style="color:#00c4cc;font-weight:700">{len(df):,}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Render pill ──────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)

if pill == "📊 General":
    general.render(df)
elif pill == "🗺️ Geográfica":
    geografica.render(df)
elif pill == "🏢 Sucursales & Empleados":
    sucursales.render(df, emp_raw)

st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="margin-top:48px;padding-top:16px;'
    f'border-top:1px solid rgba(255,255,255,0.06);'
    f'font-size:10px;color:{TEXT_MUTED};text-align:center">'
    f'CrediClub · Dashboard Analítico · Alejandro Manuel Nieto Delgado'
    f'</div>',
    unsafe_allow_html=True,
)
