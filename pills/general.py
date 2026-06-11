import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.theme import (
    apply_theme, kpi_card, section_title, fmt_currency, fmt_number,
    PRIMARY, PRIMARY_20, PRIMARY_40, BAR_COLORS, TEXT_MUTED, TEXT_MAIN, BG_CARD, BORDER
)


def render(df: pd.DataFrame):
    # ── KPIs ────────────────────────────────────────────────────────────────
    total_cartera   = df["monto_pendiente"].sum()
    prom_dias       = df["dias_atraso"].mean()
    prom_prestamo   = df["monto_prestamo"].mean()
    prom_semanal    = df["pago_semanal"].mean()
    total_monto_atr = df["monto_atrasado"].sum()
    pct_mora        = (total_monto_atr / total_cartera * 100) if total_cartera > 0 else 0
    total_creditos  = len(df)

    st.markdown(section_title("Indicadores Generales"), unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, value, sub in [
        (c1, "Cartera Total",        fmt_currency(total_cartera),  f"{total_creditos:,} créditos"),
        (c2, "Monto Atrasado",       fmt_currency(total_monto_atr),f"{pct_mora:.1f}% de cartera"),
        (c3, "Prom. Días de Atraso", f"{prom_dias:.1f}",           "días por crédito"),
        (c4, "Prom. Monto Préstamo", fmt_currency(prom_prestamo),  "por crédito"),
        (c5, "Prom. Pago Semanal",   fmt_currency(prom_semanal),   "por crédito"),
    ]:
        with col:
            st.markdown(kpi_card(label, value, sub), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauge mora + tabla por dirección ────────────────────────────────────
    st.markdown(section_title("Nivel de Mora y Resumen por Dirección"), unsafe_allow_html=True)
    col_g, col_dir = st.columns([1, 2])

    with col_g:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct_mora,
            number={"suffix": "%", "font": {"color": PRIMARY, "size": 36}},
            delta={"reference": 10, "increasing": {"color": "#ff7850"}, "decreasing": {"color": PRIMARY}},
            gauge={
                "axis": {"range": [0, 50], "tickcolor": TEXT_MUTED, "tickfont": {"color": TEXT_MUTED}},
                "bar":  {"color": PRIMARY, "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 10],  "color": "rgba(0,196,204,0.15)"},
                    {"range": [10, 25], "color": "rgba(255,200,80,0.15)"},
                    {"range": [25, 50], "color": "rgba(255,120,80,0.15)"},
                ],
                "threshold": {"line": {"color": "#ff7850", "width": 2}, "thickness": 0.75, "value": 25},
            },
            title={"text": "% Monto Atrasado / Cartera Total", "font": {"color": TEXT_MUTED, "size": 12}},
        ))
        apply_theme(gauge)
        gauge.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(gauge, use_container_width=True)

    with col_dir:
        dir_df = (
            df.groupby("subdireccion", as_index=False)
            .agg(
                creditos    =("prestamo",       "count"),
                cartera     =("monto_pendiente","sum"),
                monto_atr   =("monto_atrasado", "sum"),
                prom_prestamo=("monto_prestamo","mean"),
                prom_semanal=("pago_semanal",   "mean"),
                prom_dias   =("dias_atraso",    "mean"),
            )
        )
        dir_df["pct_mora"] = (dir_df["monto_atr"] / dir_df["cartera"] * 100).round(1)
        dir_df = dir_df.sort_values("cartera", ascending=False)

        display = dir_df.rename(columns={
            "subdireccion": "Dirección",
            "creditos":     "Créditos",
            "cartera":      "Cartera",
            "prom_prestamo":"Prom. Préstamo",
            "prom_semanal": "Prom. Semanal",
            "prom_dias":    "Prom. Días Atraso",
            "pct_mora":     "% Mora",
        })[["Dirección","Créditos","Cartera","Prom. Préstamo","Prom. Semanal","Prom. Días Atraso","% Mora"]]

        st.dataframe(
            display.style
            .format({
                "Cartera":           lambda x: fmt_currency(x),
                "Prom. Préstamo":    lambda x: fmt_currency(x),
                "Prom. Semanal":     lambda x: fmt_currency(x),
                "Prom. Días Atraso": "{:.1f}",
                "% Mora":            "{:.1f}%",
            })
            .background_gradient(subset=["% Mora"],  cmap="RdYlGn_r", vmin=0, vmax=40)
            .background_gradient(subset=["Cartera"],  cmap="Blues"),
            use_container_width=True,
            height=230,
        )

    # ── Créditos por mes ─────────────────────────────────────────────────────
    st.markdown(section_title("Créditos Otorgados por Mes"), unsafe_allow_html=True)

    mes_df = (
        df.groupby(["mes_orden","mes_nombre"], as_index=False)
        .agg(creditos=("prestamo","count"), monto=("monto_prestamo","sum"))
        .sort_values("mes_orden")
    )

    fig_mes = go.Figure()
    fig_mes.add_bar(
        x=mes_df["mes_nombre"],
        y=mes_df["creditos"],
        marker_color=PRIMARY_40,
        marker_line_color=PRIMARY,
        marker_line_width=1.5,
        hovertemplate="<b>%{x}</b><br>Créditos: %{y:,}<extra></extra>",
    )
    apply_theme(fig_mes, "Número de Créditos por Mes")
    fig_mes.update_layout(
        height=320,
        xaxis_title="Mes",
        yaxis_title="Número de Créditos",
    )
    st.plotly_chart(fig_mes, use_container_width=True)

    # ── Créditos por mes × sucursal ──────────────────────────────────────────
    st.markdown(section_title("Créditos por Mes y Sucursal"), unsafe_allow_html=True)

    top15 = df.groupby("sucursal")["prestamo"].count().nlargest(15).index.tolist()
    suc_filter = st.multiselect(
        "Seleccionar sucursales", options=top15, default=top15[:8],
        key="suc_mes_filter",
    )
    if suc_filter:
        sub_df = df[df["sucursal"].isin(suc_filter)]
        pivot = (
            sub_df.groupby(["mes_orden","mes_nombre","sucursal"], as_index=False)
            .agg(creditos=("prestamo","count"))
            .sort_values("mes_orden")
        )
        fig_suc = px.bar(
            pivot, x="mes_nombre", y="creditos", color="sucursal",
            barmode="group",
            color_discrete_sequence=BAR_COLORS,
            labels={"mes_nombre":"Mes","creditos":"Número de Créditos","sucursal":"Sucursal"},
        )
        apply_theme(fig_suc, "Créditos por Mes y Sucursal")
        fig_suc.update_layout(
            height=380,
            xaxis_tickangle=-30,
            xaxis_title="Mes",
            yaxis_title="Número de Créditos",
            legend_title_text="Sucursal",
        )
        st.plotly_chart(fig_suc, use_container_width=True)

    # ── Toggle semanal / mensual ─────────────────────────────────────────────
    st.markdown(section_title("Créditos y Monto Otorgado — Semanal / Mensual"), unsafe_allow_html=True)

    granularity = st.radio("Granularidad", ["Mensual","Semanal"], horizontal=True, key="gran_radio")

    if granularity == "Mensual":
        grp = (
            df.groupby(["mes_orden","mes_nombre"], as_index=False)
            .agg(creditos=("prestamo","count"), monto=("monto_prestamo","sum"))
            .sort_values("mes_orden")
        )
        x_col, x_label = "mes_nombre", "Mes"
    else:
        grp = (
            df.groupby(["semana_orden","semana_str"], as_index=False)
            .agg(creditos=("prestamo","count"), monto=("monto_prestamo","sum"))
            .sort_values("semana_orden")
        )
        x_col, x_label = "semana_str", "Semana"

    col_l, col_r = st.columns(2)

    with col_l:
        fig_c = go.Figure()
        fig_c.add_bar(
            x=grp[x_col], y=grp["creditos"],
            marker_color=PRIMARY_40, marker_line_color=PRIMARY, marker_line_width=1.2,
            hovertemplate=f"<b>%{{x}}</b><br>Créditos: %{{y:,}}<extra></extra>",
        )
        fig_c.add_scatter(
            x=grp[x_col], y=grp["creditos"],
            mode="lines+markers", line=dict(color=PRIMARY, width=2),
            marker=dict(size=5), hoverinfo="skip",
        )
        apply_theme(fig_c, f"Número de Créditos ({granularity})")
        fig_c.update_layout(
            height=320, xaxis_tickangle=-30, showlegend=False,
            xaxis_title=x_label, yaxis_title="Número de Créditos",
        )
        st.plotly_chart(fig_c, use_container_width=True)

    with col_r:
        fig_m = go.Figure()
        fig_m.add_bar(
            x=grp[x_col], y=grp["monto"],
            marker_color="rgba(0,200,160,0.35)", marker_line_color="#00c8a0", marker_line_width=1.2,
            hovertemplate=f"<b>%{{x}}</b><br>Monto: $%{{y:,.0f}}<extra></extra>",
        )
        fig_m.add_scatter(
            x=grp[x_col], y=grp["monto"],
            mode="lines+markers", line=dict(color="#00c8a0", width=2),
            marker=dict(size=5), hoverinfo="skip",
        )
        apply_theme(fig_m, f"Monto Otorgado ({granularity})")
        fig_m.update_layout(
            height=320, xaxis_tickangle=-30, showlegend=False,
            xaxis_title=x_label, yaxis_title="Monto Otorgado ($)",
        )
        st.plotly_chart(fig_m, use_container_width=True)

    # ── Top 10 sucursales por cartera ─────────────────────────────────────────
    st.markdown(section_title("Top 10 Sucursales por Cartera"), unsafe_allow_html=True)
    top10 = (
        df.groupby("sucursal", as_index=False)
        .agg(cartera=("monto_pendiente","sum"), creditos=("prestamo","count"))
        .nlargest(10,"cartera")
        .sort_values("cartera")
    )
    fig_top = px.bar(
        top10, x="cartera", y="sucursal",
        orientation="h",
        color="cartera",
        color_continuous_scale=[[0,"rgba(0,196,204,0.2)"],[1,PRIMARY]],
        labels={"cartera":"Cartera Total ($)","sucursal":"Sucursal"},
        custom_data=["creditos"],
        text=top10["cartera"].apply(fmt_currency),
    )
    fig_top.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=10),
        hovertemplate="<b>%{y}</b><br>Cartera: $%{x:,.0f}<br>Créditos: %{customdata[0]:,}<extra></extra>",
    )
    apply_theme(fig_top, "Top 10 Sucursales — Cartera Total")
    fig_top.update_layout(
        height=380,
        coloraxis_showscale=False,
        xaxis_title="Cartera Total ($)",
        yaxis_title="",
    )
    st.plotly_chart(fig_top, use_container_width=True)
