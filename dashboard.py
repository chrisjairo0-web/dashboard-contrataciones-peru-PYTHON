from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Dashboard Contrataciones Peru", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "contrataciones_peru_2022_2024_maestro.csv"


@st.cache_data
def cargar_datos():
    """Lee la base maestra y deja listas las columnas del dashboard."""
    df = pd.read_csv(DATA_FILE, low_memory=False)
    df["n_postores"] = pd.to_numeric(df["n_postores"], errors="coerce")
    df["monto_adjudicado"] = pd.to_numeric(df["monto_adjudicado"], errors="coerce").fillna(0)
    df["monto_MM"] = df["monto_adjudicado"] / 1_000_000
    df["un_solo_postor"] = df["un_solo_postor"].astype(str).str.lower().eq("true")
    df["fecha_proceso"] = pd.to_datetime(df["fecha_proceso"], errors="coerce")
    df["mes"] = df["fecha_proceso"].dt.to_period("M").astype(str)
    return df


df = cargar_datos()

st.title("Dashboard de Transparencia en Contrataciones Publicas del Peru")
st.caption("Analisis basado en datos OCDS de 2022, 2023 y 2024")

with st.sidebar:
    st.header("Filtros")

    anios = sorted(df["anio"].dropna().unique().tolist())
    departamentos = sorted(df["departamento"].dropna().unique().tolist())
    categorias = sorted(df["categoria"].dropna().unique().tolist())

    filtro_anios = st.multiselect("Anios", options=anios, default=anios)
    filtro_departamentos = st.multiselect("Departamentos", options=departamentos)
    filtro_categorias = st.multiselect("Categorias", options=categorias)

dash = df.copy()
if filtro_anios:
    dash = dash[dash["anio"].isin(filtro_anios)]
if filtro_departamentos:
    dash = dash[dash["departamento"].isin(filtro_departamentos)]
if filtro_categorias:
    dash = dash[dash["categoria"].isin(filtro_categorias)]

total_procesos = dash["ocid"].nunique()
pct_un_postor = dash["un_solo_postor"].mean() * 100 if len(dash) else 0
monto_total = dash["monto_MM"].sum()
pct_directa = ((dash["metodo_simple"] == "Directa").mean() * 100) if len(dash) else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total procesos", f"{total_procesos:,}")
col2.metric("% un solo postor", f"{pct_un_postor:.2f}%")
col3.metric("Monto total MM PEN", f"{monto_total:,.2f}")
col4.metric("% directas", f"{pct_directa:.2f}%")

st.subheader("Resumen General")
g1 = dash.groupby("categoria", as_index=False).agg(monto_MM=("monto_MM", "sum"))
fig1 = px.treemap(g1, path=["categoria"], values="monto_MM", title="Monto adjudicado por categoria")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Competencia")
g2 = dash["n_postores"].dropna().clip(upper=10)
fig2 = px.histogram(g2, nbins=10, title="Distribucion del numero de postores")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Riesgo Geografico")
g3 = (
    dash[dash["departamento"] != "Sin dato"]
    .groupby("departamento", as_index=False)
    .agg(casos_un_postor=("un_solo_postor", "sum"))
    .sort_values("casos_un_postor", ascending=False)
    .head(15)
)
fig3 = px.bar(
    g3,
    x="casos_un_postor",
    y="departamento",
    orientation="h",
    title="Departamentos con mas procesos de un solo postor",
)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Evolucion por Metodo")
g4 = (
    dash[dash["metodo_simple"].isin(["Competitivo", "Directa"])]
    .groupby(["mes", "metodo_simple"], as_index=False)
    .agg(procesos=("ocid", "nunique"))
)
if not g4.empty:
    g4["mes_dt"] = pd.to_datetime(g4["mes"] + "-01")
    g4 = g4.sort_values("mes_dt")
    fig4 = px.line(g4, x="mes_dt", y="procesos", color="metodo_simple", markers=True, title="Evolucion mensual por metodo")
    st.plotly_chart(fig4, use_container_width=True)
