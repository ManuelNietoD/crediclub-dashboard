import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.theme import (
    apply_theme, kpi_card, section_title, fmt_currency,
    PRIMARY, PRIMARY_40, TEXT_MUTED, BAR_COLORS
)

REGION_COORDS = {
    "NORTE":              (25.6866, -100.3161),
    "NOROESTE":           (29.0729, -110.9559),
    "CENTRO-OCCIDENTE":   (20.6597, -103.3496),
    "SUR":                (17.9869,  -92.9303),
    "ARCO - CDMX":        (19.4326,  -99.1332),
    "CENTRO":             (19.0414,  -98.2063),
    "PACIFICO":           (20.9674, -105.2664),
    "ALTRECA":            (23.6345, -102.5528),
    "AVANZA":             (21.0,    -101.0),
}


def render(df: pd.DataFrame):
    # ── KPIs por dirección ───────────────────────────────────────────────────
    st.markdown(section_title("Cartera por Dirección"), unsafe_allow_html=True)

    dir_summary = (
        df.groupby("subdireccion", as_index=False)
        .agg(cartera=("monto_pendiente","sum"), creditos=("prestamo","count"))
        .sort_values("cartera", ascending=False)
    )
    cols = st.columns(len(dir_summary))
    for col, (_, row) in zip(cols, dir_summary.iterrows()):
        with col:
            st.markdown(
                kpi_card(row["subdireccion"], fmt_currency(row["cartera"]), f"{row['creditos']:,} créditos"),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Heatmap Región × Mes ─────────────────────────────────────────────────
    st.markdown(section_title("Monto Préstamo por Región y Mes"), unsafe_allow_html=True)

    pivot = (
        df.groupby(["region","mes_orden","mes_nombre"], as_index=False)
        .agg(monto=("monto_prestamo","sum"))
        .sort_values("mes_orden")
    )
    mes_labels = (
        pivot.sort_values("mes_orden")[["mes_orden","mes_nombre"]]
        .drop_duplicates()
        .set_index("mes_orden")["mes_nombre"]
    )
    pivot_wide = pivot.pivot_table(
        index="region", columns="mes_nombre", values="monto", aggfunc="sum", fill_value=0
    )
    ordered_cols = [mes_labels[k] for k in sorted(mes_labels.index) if mes_labels[k] in pivot_wide.columns]
    pivot_wide = pivot_wide[ordered_cols]

    fig_heat = px.imshow(
        pivot_wide,
        color_continuous_scale=[[0,"rgba(0,0,0,0)"],[0.3,"rgba(0,196,204,0.3)"],[1,PRIMARY]],
        aspect="auto",
        labels={"color":"Monto Préstamo ($)", "x":"Mes", "y":"Región"},
        text_auto=".2s",
    )
    fig_heat.update_traces(
        textfont=dict(color="white", size=10),
        hovertemplate="<b>Región:</b> %{y}<br><b>Mes:</b> %{x}<br><b>Monto:</b> $%{z:,.0f}<extra></extra>",
    )
    apply_theme(fig_heat, "Suma de Monto Préstamo por Región y Mes")
    fig_heat.update_layout(
        height=420,
        xaxis=dict(title="Mes", tickangle=-30, tickfont=dict(color=TEXT_MUTED, size=11)),
        yaxis=dict(title="Región", tickfont=dict(color=TEXT_MUTED, size=11)),
        coloraxis_colorbar=dict(
            title=dict(text="Monto ($)", font=dict(color=TEXT_MUTED)),
            tickfont=dict(color=TEXT_MUTED),
        ),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── Mapa burbuja ─────────────────────────────────────────────────────────
    st.markdown(section_title("Mapa — Cartera por Dirección"), unsafe_allow_html=True)

    map_df = (
        df.groupby("subdireccion", as_index=False)
        .agg(
            cartera  =("monto_pendiente","sum"),
            creditos =("prestamo",       "count"),
            monto_atr=("monto_atrasado", "sum"),
        )
    )
    map_df["lat"]      = map_df["subdireccion"].map(lambda x: REGION_COORDS.get(x,(23.6,-102.5))[0])
    map_df["lon"]      = map_df["subdireccion"].map(lambda x: REGION_COORDS.get(x,(23.6,-102.5))[1])
    map_df["pct_mora"] = (map_df["monto_atr"] / map_df["cartera"] * 100).round(1)

    fig_map = px.scatter_mapbox(
        map_df,
        lat="lat", lon="lon",
        size="cartera",
        color="pct_mora",
        color_continuous_scale=[[0,PRIMARY],[0.5,"rgba(255,200,80,0.8)"],[1,"#ff7850"]],
        size_max=70,
        hover_name="subdireccion",
        hover_data={
            "cartera":  ":.0f",
            "creditos": True,
            "pct_mora": ":.1f",
            "lat": False, "lon": False,
        },
        labels={"pct_mora":"% Mora","cartera":"Cartera ($)","creditos":"Créditos"},
        mapbox_style="carto-darkmatter",
        center={"lat":23.6,"lon":-102.5},
        zoom=4.2,
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=500,
        margin=dict(l=0,r=0,t=0,b=0),
        coloraxis_colorbar=dict(
            title=dict(text="% Mora", font=dict(color=TEXT_MUTED)),
            tickfont=dict(color=TEXT_MUTED),
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("🟢 Verde = mora baja · 🟡 Amarillo = mora media · 🔴 Rojo = mora alta  |  Tamaño de burbuja = cartera total")

    # ── Pago semanal promedio por dirección ──────────────────────────────────
    st.markdown(section_title("Pago Semanal Promedio por Dirección"), unsafe_allow_html=True)

    pago_dir = (
        df.groupby("subdireccion", as_index=False)
        .agg(prom_semanal=("pago_semanal","mean"))
        .sort_values("prom_semanal")
    )
    fig_semanal = px.bar(
        pago_dir, x="prom_semanal", y="subdireccion",
        orientation="h",
        color="prom_semanal",
        color_continuous_scale=[[0,"rgba(0,196,204,0.2)"],[1,PRIMARY]],
        labels={"prom_semanal":"Pago Semanal Promedio ($)","subdireccion":"Dirección"},
        text=pago_dir["prom_semanal"].apply(fmt_currency),
    )
    fig_semanal.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT_MUTED, size=11),
        hovertemplate="<b>%{y}</b><br>Pago Semanal Promedio: $%{x:,.0f}<extra></extra>",
    )
    apply_theme(fig_semanal, "Promedio de Pago Semanal por Dirección")
    fig_semanal.update_layout(
        height=340,
        coloraxis_showscale=False,
        xaxis_title="Pago Semanal Promedio ($)",
        yaxis_title="Dirección",
    )
    st.plotly_chart(fig_semanal, use_container_width=True)

    # ── Treemap ──────────────────────────────────────────────────────────────
    st.markdown(section_title("Distribución de Cartera — Dirección · Región · Sucursal"), unsafe_allow_html=True)

    tree_df = (
        df.groupby(["subdireccion","region","sucursal"], as_index=False)
        .agg(cartera=("monto_pendiente","sum"))
    )
    fig_tree = px.treemap(
        tree_df,
        path=["subdireccion","region","sucursal"],
        values="cartera",
        color="cartera",
        color_continuous_scale=[[0,"rgba(0,196,204,0.2)"],[0.5,"rgba(0,196,204,0.6)"],[1,PRIMARY]],
        labels={"cartera":"Cartera ($)"},
    )
    fig_tree.update_traces(
        textfont=dict(color="white"),
        hovertemplate="<b>%{label}</b><br>Cartera: $%{value:,.0f}<extra></extra>",
    )
    apply_theme(fig_tree, "Distribución de Cartera por Dirección / Región / Sucursal")
    fig_tree.update_layout(
        height=500,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=40,b=0),
    )
    st.plotly_chart(fig_tree, use_container_width=True)
