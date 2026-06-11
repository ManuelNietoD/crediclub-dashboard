import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

DATA_PATH = Path(__file__).parent.parent / "data" / "data.xlsx"


@st.cache_data
def load_data() -> pd.DataFrame:
    # 1. Read sheets — openpyxl parses FechaInicio as datetime directly
    balance   = pd.read_excel(DATA_PATH, sheet_name="BalanceDiario", engine="openpyxl")
    empleados = pd.read_excel(DATA_PATH, sheet_name="Empleados",     engine="openpyxl")
    sucursales= pd.read_excel(DATA_PATH, sheet_name="Sucursales",    engine="openpyxl")

    # 2. BalanceDiario — rename & types
    balance.columns = balance.columns.str.strip()
    balance = balance.rename(columns={
        "FechaInicio":   "fecha_inicio",
        "Prestamo":      "prestamo",
        "# de Pagos":    "num_pagos",
        "Pago semanal":  "pago_semanal",
        "MontoPendiente":"monto_pendiente",
        "Dias de atraso":"dias_atraso",
        "Monto Atrasado":"monto_atrasado",
        "EmpleadoID":    "empleado_id",
        "Monto Préstamo":"monto_prestamo",
    })
    balance["fecha_inicio"] = pd.to_datetime(balance["fecha_inicio"])
    for c in ["pago_semanal", "monto_pendiente", "monto_atrasado", "monto_prestamo"]:
        balance[c] = pd.to_numeric(balance[c], errors="coerce").astype(float)
    for c in ["num_pagos", "dias_atraso", "empleado_id", "prestamo"]:
        balance[c] = pd.to_numeric(balance[c], errors="coerce").astype("Int64")

    # 3. Empleados — rename & types
    empleados.columns = empleados.columns.str.strip()
    empleados = empleados.rename(columns={
        "EmpleadoID": "empleado_id",
        "SucursalID": "sucursal_id",
        "Activo":     "activo",
    })
    for c in ["empleado_id", "sucursal_id"]:
        empleados[c] = pd.to_numeric(empleados[c], errors="coerce").astype("Int64")

    # 4. Sucursales — rename & types
    sucursales.columns = sucursales.columns.str.strip()
    sucursales = sucursales.rename(columns={
        "SucursalID":  "sucursal_id",
        "Sucursal":    "sucursal",
        "Region":      "region",
        "Subdireccion":"subdireccion",
    })
    sucursales["sucursal_id"] = pd.to_numeric(sucursales["sucursal_id"], errors="coerce").astype("Int64")

    # 5. Join: BalanceDiario → Empleados → Sucursales
    df = (
        balance
        .merge(empleados[["empleado_id", "sucursal_id"]], on="empleado_id", how="left")
        .merge(sucursales, on="sucursal_id", how="left")
    )

    # 6. Null imputation (branches without match → ALTRECA)
    df["region"]      = df["region"].fillna("ALTRECA")
    df["subdireccion"]= df["subdireccion"].fillna("ALTRECA")
    df["sucursal"]    = df["sucursal"].fillna("SIN SUCURSAL")

    # 7. Time dimensions
    df["anio"]        = df["fecha_inicio"].dt.year
    df["mes_num"]     = df["fecha_inicio"].dt.month
    df["mes_nombre"]  = df["fecha_inicio"].dt.strftime("%b %Y")
    df["mes_orden"]   = df["fecha_inicio"].dt.to_period("M").apply(lambda p: p.ordinal)
    df["semana_str"]  = df["fecha_inicio"].dt.strftime("S%W %Y")
    df["semana_orden"]= df["fecha_inicio"].dt.to_period("W").apply(lambda p: p.ordinal)

    # 8. Derived KPIs
    df["tiene_atraso"] = (df["dias_atraso"] > 0).astype(int)
    df["pct_atrasado"] = np.where(
        df["monto_pendiente"] > 0,
        df["monto_atrasado"] / df["monto_pendiente"] * 100,
        0.0,
    )

    return df


@st.cache_data
def load_empleados_raw() -> pd.DataFrame:
    emp = pd.read_excel(DATA_PATH, sheet_name="Empleados", engine="openpyxl")
    emp.columns = emp.columns.str.strip()
    emp = emp.rename(columns={
        "EmpleadoID": "empleado_id",
        "SucursalID": "sucursal_id",
        "Activo":     "activo",
    })
    return emp
