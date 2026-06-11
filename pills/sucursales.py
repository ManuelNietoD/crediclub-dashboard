import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.theme import (
    apply_theme, kpi_card, section_title, fmt_currency, fmt_number,
    PRIMARY, PRIMARY_40, BAR_COLORS, TEXT_MUTED, TEXT_MAIN,
)


def render(df: pd.DataFrame, emp_raw: pd.DataFrame):
    # ── Filters sidebar ─────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f'<div style="color:{TEXT_MUTED};font-size:12px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">Filtros — Sucursales</div>', unsafe_allow_html=True)

        dirs_available = sorted(df["subdireccion"].unique())
        selected_dir = st.multiselect("Dirección", dirs_available, default=dirs_available, key="suc_dir")

        df_f = df[df["subdireccion"].isin(selected_dir)] if selected_dir else df

        regs_available = sorted(df_f["region"].unique())
        selected_reg = st.multiselect("Región", regs_available, default=regs_available, key="suc_reg")
        df_f = df_f[df_f["region"].isin(selected_reg)] if selected_reg else df_f

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.markdown(section_title("Indicadores de Sucursales"), unsafe_allow_html=True)

    total_suc    = df_f["sucursal"].nunique()
    total_emp    = emp_raw["empleado_id"].nunique()
    emp_activos  = emp_raw[emp_raw["activo"] == 1]["empleado_id"].nunique()
    total_cred   = len(df_f)
    total_cart   = df_f["monto_pendiente"].sum()
    total_atr    = df_f["monto_atrasado"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, sub in [
        (c1, "Sucursales", f"{total_suc}", "en filtro"),
        (c2, "Empleados Activos", f"{emp_activos:,}", f"de {total_emp:,} totales"),
        (c3, "Créditos", f"{total_cred:,}", "en filtro"),
        (c4, "Cartera Total", fmt_currency(total_cart), "monto pendiente"),
        (c5, "Monto Atrasado", fmt_currency(total_atr),
         f"{(total_atr/total_cart*100):.1f}% de cartera" if total_cart else "—"),
    ]:
        with col:
            st.markdown(kpi_card(label, val, sub), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Créditos por sucursal mes a mes ──────────────────────────────────────
    st.markdown(section_title("Créditos Totales por Sucursal — Mes a Mes"), unsafe_allow_html=True)

    top_n = st.slider("Top N sucursales", 5, 30, 12, key="top_n_suc")
    top_suc = df_f.groupby("sucursal")["prestamo"].count().nlargest(top_n).index.tolist()
    pivot_suc = (
        df_f[df_f["sucursal"].isin(top_suc)]
        .groupby(["mes_orden", "mes_nombre", "sucursal"], as_index=False)
        .agg(creditos=("prestamo", "count"))
        .sort_values("mes_orden")
    )

    fig_suc = px.bar(
        pivot_suc, x="mes_nombre", y="creditos", color="sucursal",
        barmode="group",
        color_discrete_sequence=BAR_COLORS * 3,
        labels={"mes_nombre": "Mes", "creditos": "Créditos", "sucursal": "Sucursal"},
    )
    apply_theme(fig_suc, f"Créditos por Mes — Top {top_n} Sucursales")
    fig_suc.update_layout(height=400, xaxis_tickangle=-30,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="left", x=0))
    st.plotly_chart(fig_suc, use_container_width=True)

    # ── % monto atrasado vs colocado por sucursal ─────────────────────────────
    st.markdown(section_title("% Mora por Sucursal (Monto Atrasado / Monto Colocado)"), unsafe_allow_html=True)

    mora_suc = (
        df_f.groupby("sucursal", as_index=False)
        .agg(
            monto_colocado=("monto_prestamo", "sum"),
            monto_atr=("monto_atrasado", "sum"),
            creditos=("prestamo", "count"),
        )
        .assign(pct_mora=lambda d: (d["monto_atr"] / d["monto_colocado"] * 100).round(2))
        .nlargest(20, "pct_mora")
        .sort_values("pct_mora")
    )

    fig_mora = px.bar(
        mora_suc, x="pct_mora", y="sucursal",
        orientation="h",
        color="pct_mora",
        color_continuous_scale=[[0, "rgba(0,196,204,0.6)"], [0.5, "rgba(255,200,80,0.8)"], [1, "#ff7850"]],
        labels={"pct_mora": "% Mora", "sucursal": ""},
        custom_data=["creditos", "monto_atr", "monto_colocado"],
        text=mora_suc["pct_mora"].apply(lambda x: f"{x:.1f}%"),
    )
    fig_mora.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=10),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "% Mora: %{x:.1f}%<br>"
            "Monto Atrasado: $%{customdata[1]:,.0f}<br>"
            "Monto Colocado: $%{customdata[2]:,.0f}<br>"
            "Créditos: %{customdata[0]:,}<extra></extra>"
        ),
    )
    apply_theme(fig_mora, "Top 20 Sucursales — % Mora (Mayor a Menor)")
    fig_mora.update_layout(height=560, coloraxis_showscale=False)
    st.plotly_chart(fig_mora, use_container_width=True)

    # ── Ranking tabla ─────────────────────────────────────────────────────────
    st.markdown(section_title("Ranking Completo de Sucursales"), unsafe_allow_html=True)

    ranking = (
        df_f.groupby(["sucursal", "region", "subdireccion"], as_index=False)
        .agg(
            creditos=("prestamo", "count"),
            cartera=("monto_pendiente", "sum"),
            monto_colocado=("monto_prestamo", "sum"),
            monto_atr=("monto_atrasado", "sum"),
            prom_semanal=("pago_semanal", "mean"),
            prom_dias=("dias_atraso", "mean"),
        )
        .assign(pct_mora=lambda d: (d["monto_atr"] / d["monto_colocado"] * 100).round(1))
        .sort_values("cartera", ascending=False)
        .reset_index(drop=True)
    )
    ranking.index = ranking.index + 1

    col_sort = st.selectbox(
        "Ordenar por", ["Cartera", "Créditos", "% Mora", "Monto Colocado"],
        key="rank_sort"
    )
    sort_map = {
        "Cartera": "cartera", "Créditos": "creditos",
        "% Mora": "pct_mora", "Monto Colocado": "monto_colocado",
    }
    ranking = ranking.sort_values(sort_map[col_sort], ascending=False).reset_index(drop=True)
    ranking.index = ranking.index + 1

    display = ranking.rename(columns={
        "sucursal": "Sucursal", "region": "Región", "subdireccion": "Dirección",
        "creditos": "Créditos", "cartera": "Cartera",
        "monto_colocado": "Monto Colocado", "monto_atr": "Monto Atrasado",
        "prom_semanal": "Prom. Semanal", "prom_dias": "Prom. Días",
        "pct_mora": "% Mora",
    })[["Sucursal", "Dirección", "Región", "Créditos", "Cartera",
        "Monto Colocado", "Monto Atrasado", "% Mora", "Prom. Días"]]

    st.dataframe(
        display.style
        .format({
            "Cartera": lambda x: fmt_currency(x),
            "Monto Colocado": lambda x: fmt_currency(x),
            "Monto Atrasado": lambda x: fmt_currency(x),
            "% Mora": "{:.1f}%",
            "Prom. Días": "{:.1f}",
        })
        .background_gradient(subset=["% Mora"], cmap="RdYlGn_r", vmin=0, vmax=50)
        .background_gradient(subset=["Cartera"], cmap="Blues"),
        use_container_width=True,
        height=420,
    )

    # ── Scatter: cartera vs mora ──────────────────────────────────────────────
    st.markdown(section_title("Dispersión — Cartera vs % Mora por Sucursal"), unsafe_allow_html=True)

    fig_sc = px.scatter(
        ranking.rename(columns={"Sucursal": "sucursal", "Cartera": "cartera",
                                "% Mora": "pct_mora", "Créditos": "creditos",
                                "Dirección": "subdireccion"}),
        x="cartera", y="pct_mora",
        size="creditos", color="subdireccion",
        color_discrete_sequence=BAR_COLORS * 2,
        hover_name="sucursal",
        labels={"cartera": "Cartera Total", "pct_mora": "% Mora", "creditos": "Créditos"},
        size_max=40,
    )
    apply_theme(fig_sc, "Cartera Total vs % Mora — tamaño = número de créditos")
    fig_sc.update_layout(height=420)
    st.plotly_chart(fig_sc, use_container_width=True)
