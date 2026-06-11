# CrediClub · Dashboard Analítico

Dashboard interactivo de crédito construido con **Streamlit + Plotly**.

## Estructura

```
crediclub-dashboard/
├── app.py                    # Entrada principal
├── pills/
│   ├── general.py            # Pill 1 — KPIs, créditos, monto
│   ├── geografica.py         # Pill 2 — Heatmap, mapa, treemap
│   └── sucursales.py         # Pill 3 — Ranking, mora, scatter
├── utils/
│   ├── data_loader.py        # ETL: join de 3 tablas, tipos, fechas
│   └── theme.py              # Colores CrediClub, CSS, helpers
├── assets/
│   └── logo.jpg
├── data/
│   └── data.xlsx
├── .streamlit/
│   └── config.toml
└── requirements.txt
```

## Métricas implementadas (Ejercicio 2)

| Métrica | Pill | Visualización |
|---|---|---|
| Suma total cartera (Monto Pendiente) | General | KPI Card |
| Promedio días de atraso | General | KPI Card + Gauge de mora |
| Promedio monto préstamo | General | KPI Card |
| Promedio pago semanal | General | KPI Card |
| Créditos por mes | General | Bar chart |
| Créditos por mes × sucursal | General | Bar chart agrupado + filtro |
| Créditos otorgados semanal/mensual | General | Bar + línea (toggle) |
| Monto otorgado semanal/mensual | General | Bar + línea (toggle) |
| Resumen métricas por Dirección | General | Tabla estilizada |
| Top 10 sucursales por cartera | General | Bar horizontal |
| Suma Monto Préstamo × Región × Mes | Geográfica | Heatmap |
| Mapa de México por Dirección | Geográfica | Mapa burbuja (Mapbox) |
| Monto promedio pago semanal × Dirección | Geográfica | Bar horizontal |
| Treemap Dirección → Región → Sucursal | Geográfica | Treemap drill-down |
| Créditos totales por sucursal mes a mes | Sucursales | Bar agrupado |
| % mora por sucursal | Sucursales | Bar horizontal con color condicional |
| Ranking completo de sucursales | Sucursales | Tabla interactiva |
| Cartera vs % mora scatter | Sucursales | Bubble scatter |
