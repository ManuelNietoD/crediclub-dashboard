import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.theme import (
    apply_theme, kpi_card, section_title, fmt_currency,
    PRIMARY, PRIMARY_40, PALETTE_SUCURSALES, PALETTE_DIRECCIONES, TEXT_MUTED,
)


def render(df: pd.DataFrame, emp_raw: pd.DataFrame):
    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown(section_title("Indicadores de Sucursales"), unsafe_allow_html=True)

    total_suc   = df["sucursal"].nunique()
    emp_activos = emp_raw[emp_raw["activo"] == 1]["empleado_id"].nunique()
    total_emp   = emp_raw["empleado_id"].nunique()
    total_cred  = len(df)
    total_cart  = df["monto_pendiente"].sum()
    total_atr   = df["monto_atrasado"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, sub in [
        (c1, "Sucursales",        f"{total_suc}",         "en total"),
        (c2, "Empleados Activos", f"{emp_activos:,}",     f"de {total_emp:,} totales"),
        (c3, "Créditos",          f"{total_cred:,}",      "registros"),
        (c4, "Cartera Total",     fmt_currency(total_cart),"monto pendiente"),
        (c5, "Monto Atrasado",    fmt_currency(total_atr),
         f"{(total_atr/total_cart*100):.1f}% de cartera" if total_cart else "—"),
    ]:
        with col:
            st.markdown(kpi_card(label, val, sub), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Créditos por sucursal mes a mes — paleta de sucursales ────────────────
    st.markdown(section_title("Créditos por Sucursal — Mes a Mes"), unsafe_allow_html=True)

    top_n = st.slider("Número de sucursales a mostrar", 5, 25, 10, key="top_n_suc")
    top_suc = df.groupby("sucursal")["prestamo"].count().nlargest(top_n).index.tolist()
    pivot_suc = (
        df[df["sucursal"].isin(top_suc)]
        .groupby(["mes_orden","mes_nombre","sucursal"], as_index=False)
        .agg(creditos=("prestamo","count"))
        .sort_values("mes_orden")
    )
    fig_suc = px.bar(
        pivot_suc, x="mes_nombre", y="creditos", color="sucursal",
        barmode="group",
        color_discrete_sequence=PALETTE_SUCURSALES,
        labels={"mes_nombre":"Mes","creditos":"Número de Créditos","sucursal":"Sucursal"},
    )
    apply_theme(fig_suc, f"Créditos por Mes — Top {top_n} Sucursales")
    fig_suc.update_layout(
        height=420, xaxis_tickangle=-30,
        xaxis_title="Mes", yaxis_title="Número de Créditos",
        legend_title_text="Sucursal",
        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="left", x=0),
    )
    st.plotly_chart(fig_suc, use_container_width=True)

    # ── % mora por sucursal — semáforo rojo/amarillo/verde ────────────────────
    st.markdown(section_title("% Mora por Sucursal — Monto Atrasado / Monto Colocado"), unsafe_allow_html=True)

    mora_suc = (
        df.groupby("sucursal", as_index=False)
        .agg(monto_colocado=("monto_prestamo","sum"),
             monto_atr=("monto_atrasado","sum"),
             creditos=("prestamo","count"))
        .assign(pct_mora=lambda d: (d["monto_atr"] / d["monto_colocado"] * 100).round(2))
        .nlargest(20,"pct_mora").sort_values("pct_mora")
    )
    fig_mora = px.bar(
        mora_suc, x="pct_mora", y="sucursal", orientation="h",
        color="pct_mora",
        color_continuous_scale=[[0,"rgba(0,196,204,0.7)"],[0.4,"rgba(255,200,80,0.85)"],[1,"#ff5555"]],
        labels={"pct_mora":"% Mora","sucursal":"Sucursal"},
        custom_data=["creditos","monto_atr","monto_colocado"],
        text=mora_suc["pct_mora"].apply(lambda x: f"{x:.1f}%"),
    )
    fig_mora.update_traces(
        textposition="outside", textfont=dict(color=TEXT_MUTED, size=10),
        hovertemplate=(
            "<b>%{y}</b><br>% Mora: %{x:.1f}%<br>"
            "Monto Atrasado: $%{customdata[1]:,.0f}<br>"
            "Monto Colocado: $%{customdata[2]:,.0f}<br>"
            "Créditos: %{customdata[0]:,}<extra></extra>"
        ),
    )
    apply_theme(fig_mora, "Top 20 Sucursales con Mayor % de Mora")
    fig_mora.update_layout(height=560, coloraxis_showscale=False,
                           xaxis_title="% de Mora", yaxis_title="")
    st.plotly_chart(fig_mora, use_container_width=True)

    # ── Ranking tabla ─────────────────────────────────────────────────────────
    st.markdown(section_title("Ranking de Sucursales"), unsafe_allow_html=True)

    ranking = (
        df.groupby(["sucursal","region","subdireccion"], as_index=False)
        .agg(creditos=("prestamo","count"), cartera=("monto_pendiente","sum"),
             monto_colocado=("monto_prestamo","sum"), monto_atr=("monto_atrasado","sum"),
             prom_semanal=("pago_semanal","mean"), prom_dias=("dias_atraso","mean"))
        .assign(pct_mora=lambda d: (d["monto_atr"] / d["monto_colocado"] * 100).round(1))
    )
    col_sort = st.selectbox("Ordenar por",
        ["Cartera","Créditos","% Mora","Monto Colocado"], key="rank_sort")
    sort_map = {"Cartera":"cartera","Créditos":"creditos",
                "% Mora":"pct_mora","Monto Colocado":"monto_colocado"}
    ranking = ranking.sort_values(sort_map[col_sort], ascending=False).reset_index(drop=True)
    ranking.index = ranking.index + 1

    display = ranking.rename(columns={
        "sucursal":"Sucursal","region":"Región","subdireccion":"Dirección",
        "creditos":"Créditos","cartera":"Cartera","monto_colocado":"Monto Colocado",
        "monto_atr":"Monto Atrasado","prom_semanal":"Prom. Pago Semanal",
        "prom_dias":"Prom. Días Atraso","pct_mora":"% Mora",
    })[["Sucursal","Dirección","Región","Créditos","Cartera",
        "Monto Colocado","Monto Atrasado","% Mora","Prom. Días Atraso"]]

    st.dataframe(
        display.style
        .format({
            "Cartera":           lambda x: fmt_currency(x),
            "Monto Colocado":    lambda x: fmt_currency(x),
            "Monto Atrasado":    lambda x: fmt_currency(x),
            "% Mora":            "{:.1f}%",
            "Prom. Días Atraso": "{:.1f}",
        })
        .background_gradient(subset=["% Mora"],  cmap="RdYlGn_r", vmin=0, vmax=50)
        .background_gradient(subset=["Cartera"],  cmap="Blues"),
        use_container_width=True, height=420,
    )

    # ── Scatter cartera vs mora — color por dirección ─────────────────────────
    st.markdown(section_title("Dispersión — Cartera vs % Mora por Sucursal"), unsafe_allow_html=True)

    scatter_df = ranking.rename(columns={
        "Sucursal":"sucursal","Cartera":"cartera",
        "% Mora":"pct_mora","Créditos":"creditos","Dirección":"direccion",
    })[["sucursal","cartera","pct_mora","creditos","direccion"]].copy()

    fig_sc = px.scatter(
        scatter_df,
        x="cartera", y="pct_mora",
        size="creditos", color="direccion",
        color_discrete_sequence=PALETTE_DIRECCIONES,
        hover_name="sucursal",
        labels={"cartera":"Cartera Total ($)","pct_mora":"% de Mora",
                "creditos":"Créditos","direccion":"Dirección"},
        size_max=45,
    )
    apply_theme(fig_sc, "Cartera Total vs % Mora — tamaño = número de créditos")
    fig_sc.update_layout(height=440, xaxis_title="Cartera Total ($)",
                         yaxis_title="% de Mora", legend_title_text="Dirección")
    st.plotly_chart(fig_sc, use_container_width=True)
