from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.express as px
import streamlit as st


# ============================================================
# 1. CONFIGURACION GENERAL
# ============================================================

# Esta línea configura la página de Streamlit.
st.set_page_config(
    page_title="Dashboard de Contrataciones del Perú",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊",
)

# Título principal del dashboard.
st.title("Análisis de contrataciones públicas del Perú")

# Texto corto de presentación.
st.write(
    "Este dashboard resume los resultados del análisis de contrataciones públicas "
    "del Perú para los años 2022, 2023 y 2024."
)


# ============================================================
# 2. RUTA DEL ARCHIVO CSV
# ============================================================

# Path(__file__) representa la ruta del archivo actual.
# .resolve() obtiene la ruta completa.
# .parent nos lleva a la carpeta donde está guardado dashboard.py.
BASE_DIR = Path(__file__).resolve().parent

# Construimos la ruta de la carpeta data.
DATA_DIR = BASE_DIR / "data"

# Construimos la ruta exacta del archivo CSV principal.
DATA_FILE = DATA_DIR / "contrataciones_peru_2022_2024_maestro.csv"


# ============================================================
# 3. FUNCION PARA CARGAR Y LIMPIAR LOS DATOS
# ============================================================

# @st.cache_data hace que la data se cargue una sola vez.
# Así el dashboard corre más rápido cuando movemos filtros.
@st.cache_data
def load_data():
    # Leemos el archivo CSV principal.
    df = pd.read_csv(DATA_FILE, low_memory=False)

    # Si la base viniera con "anio", la renombramos a "año".
    if "anio" in df.columns and "año" not in df.columns:
        df = df.rename(columns={"anio": "año"})

    # Convertimos variables numéricas para evitar errores en gráficos.
    df["monto_adjudicado"] = pd.to_numeric(df["monto_adjudicado"], errors="coerce").fillna(0)
    df["n_postores"] = pd.to_numeric(df["n_postores"], errors="coerce")

    # Creamos una columna en millones de soles para que los montos
    # sean más fáciles de leer.
    df["monto_MM"] = df["monto_adjudicado"] / 1_000_000

    # Creamos la variable booleana "un_solo_postor".
    # Será True si el número de postores es igual a 1.
    df["un_solo_postor"] = df["n_postores"].eq(1)

    # Creamos una variable booleana para identificar contrataciones directas.
    # Si el texto contiene "direct", entonces será True.
    df["directa"] = df["metodo_simple"].astype(str).str.contains("direct", case=False, na=False)

    # Convertimos la fecha del proceso a formato fecha.
    df["fecha_proceso"] = pd.to_datetime(df["fecha_proceso"], errors="coerce")

    # Guardamos una columna auxiliar de fecha, igual que en el notebook.
    df["fecha"] = df["fecha_proceso"]

    # Extraemos el número de mes de la fecha.
    mes_numero = df["fecha"].dt.month.fillna(1).astype(int).astype(str).str.zfill(2)

    # Construimos el mes de reporte con el año oficial del análisis.
    # Así evitamos que el gráfico se vaya a años históricos como 2015.
    df["mes_reporte"] = pd.to_datetime(
        df["año"].astype(int).astype(str) + "-" + mes_numero + "-01",
        errors="coerce",
    )

    # Limpiamos columnas de texto que vamos a usar en filtros y gráficos.
    columnas_texto = [
        "categoria",
        "metodo_simple",
        "departamento",
        "entidad_compradora",
        "proveedor_ganador",
    ]

    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].fillna("Sin dato")
            df[col] = df[col].astype(str).str.strip()

    # Retornamos el DataFrame ya listo.
    return df


# Cargamos la data llamando a la función.
df = load_data()


# ============================================================
# 4. FUNCION AUXILIAR PARA QUITAR "SIN DATO"
# ============================================================

# Esta función devuelve True solo para valores que sí queremos
# mostrar en filtros y gráficos.
def es_valor_visible(serie):
    invalidos = {"Sin dato", "", "nan", "None"}
    return ~serie.astype(str).str.strip().isin(invalidos)


# Configuración simple de Seaborn para que los gráficos se vean limpios.
sns.set_theme(style="whitegrid")


# ============================================================
# 5. SIDEBAR
# ============================================================

# Definimos el título del panel lateral.
st.sidebar.header("Secciones")

# Igual que en app2.py, usamos un selectbox para elegir la sección.
opciones = st.sidebar.selectbox(
    "Seleccione una sección",
    ["Resumen general", "Competencia", "Riesgo económico", "Transparencia geográfica"],
)


# ============================================================
# 6. FILTROS
# ============================================================

st.sidebar.markdown("### Filtros")

# Sacamos los valores únicos de cada variable para los filtros.
anios = sorted(df["año"].dropna().unique())
categorias = sorted(df.loc[es_valor_visible(df["categoria"]), "categoria"].dropna().unique())
departamentos = sorted(df.loc[es_valor_visible(df["departamento"]), "departamento"].dropna().unique())

# Filtro por año.
selected_anios = st.sidebar.multiselect(
    "Año",
    options=anios,
    default=anios,
)

# Filtro por categoría.
selected_categorias = st.sidebar.multiselect(
    "Categoría",
    options=categorias,
    default=categorias,
)

# Filtro por departamento.
selected_departamentos = st.sidebar.multiselect(
    "Departamento",
    options=departamentos,
    default=departamentos,
)


# ============================================================
# 7. FILTRAR EL DATASET
# ============================================================

# Aplicamos los filtros seleccionados por el usuario.
df_filtered = df[
    (df["año"].isin(selected_anios))
    & (df["categoria"].isin(selected_categorias))
    & (df["departamento"].isin(selected_departamentos))
].copy()

# Si no hay datos luego de filtrar, mostramos una advertencia.
if df_filtered.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()


# ============================================================
# 8. INDICADORES GENERALES
# ============================================================

# Calculamos cuatro indicadores para mostrar arriba del dashboard.
total_procesos = df_filtered["ocid"].nunique()
total_monto = df_filtered["monto_MM"].sum()
pct_un_postor = df_filtered["un_solo_postor"].mean() * 100
pct_directa = df_filtered["directa"].mean() * 100

# Mostramos el nombre de la sección elegida.
st.subheader(f"Sección: {opciones}")

# Igual que en clase, usamos columns para organizar el espacio.
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric("Procesos analizados", f"{total_procesos:,}")

with col_kpi2:
    st.metric("Monto total (MM PEN)", f"{total_monto:,.2f}")

with col_kpi3:
    st.metric("% con un solo postor", f"{pct_un_postor:.2f}%")

with col_kpi4:
    st.metric("% contratación directa", f"{pct_directa:.2f}%")


# ============================================================
# 9. SECCION: RESUMEN GENERAL
# ============================================================

if opciones == "Resumen general":
    # En esta sección usamos dos filas con dos gráficos cada una.
    col1, col2 = st.columns(2)

    with col1:
        st.write("Monto adjudicado por categoría")

        g1 = (
            df_filtered[es_valor_visible(df_filtered["categoria"])]
            .groupby("categoria")["monto_MM"]
            .sum()
            .reset_index()
            .sort_values("monto_MM", ascending=False)
        )

        fig, ax = plt.subplots(figsize=(8, 5))
        g1_plot = g1.set_index("categoria")["monto_MM"].sort_values()
        g1_plot.plot(kind="barh", color="steelblue", ax=ax)
        ax.set_title("Monto adjudicado por categoría")
        ax.set_xlabel("Millones de PEN")
        ax.set_ylabel("Categoría")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.write("Procesos por año")

        g2 = (
            df_filtered.groupby("año")["ocid"]
            .nunique()
            .reset_index(name="procesos")
        )

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=g2, x="año", y="procesos", color="steelblue", ax=ax)
        ax.set_title("Cantidad de procesos por año")
        ax.set_xlabel("Año")
        ax.set_ylabel("Procesos")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.write("Participación de procesos por método")

        g3 = (
            df_filtered[es_valor_visible(df_filtered["metodo_simple"])]
            .groupby("metodo_simple")["ocid"]
            .nunique()
            .reset_index(name="procesos")
        )

        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(g3["procesos"], labels=g3["metodo_simple"], autopct="%1.1f%%", startangle=90)
        ax.set_title("Participación de procesos por método")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.write("Monto adjudicado por año y categoría")

        g4 = (
            df_filtered[es_valor_visible(df_filtered["categoria"])]
            .groupby(["año", "categoria"])["monto_MM"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            g4,
            x="año",
            y="monto_MM",
            color="categoria",
            barmode="group",
            title="Monto adjudicado por año y categoría",
            labels={"año": "Año", "monto_MM": "Millones de PEN", "categoria": "Categoría"},
            color_discrete_map={"Bienes": "#61d6a3", "Servicios": "#6ea8fe", "Obras": "#ff6658"},
        )

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 10. SECCION: COMPETENCIA
# ============================================================

elif opciones == "Competencia":
    col1, col2 = st.columns(2)

    with col1:
        st.write("Distribución del número de postores")

        g5 = df_filtered[df_filtered["n_postores"] > 0].copy()
        g5["n_postores_grafico"] = g5["n_postores"].clip(upper=10)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(g5["n_postores_grafico"], bins=10, color="salmon", edgecolor="black")
        ax.set_title("Distribución del número de postores por proceso")
        ax.set_xlabel("Número de postores (10 representa 10 o más)")
        ax.set_ylabel("Frecuencia")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.write("Porcentaje de procesos con un solo postor por año")

        g6 = (
            df_filtered.groupby("año")["un_solo_postor"]
            .mean()
            .mul(100)
            .reset_index(name="porcentaje")
        )

        fig, ax = plt.subplots(figsize=(8, 5))
        g6_plot = g6.set_index("año")["porcentaje"]
        g6_plot.plot(kind="bar", color="indianred", ax=ax)
        ax.set_title("Porcentaje de procesos con un solo postor por año")
        ax.set_xlabel("Año")
        ax.set_ylabel("Porcentaje")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.write("Top 15 departamentos con un solo postor")

        g7 = (
            df_filtered[
                (df_filtered["un_solo_postor"] == True)
                & (es_valor_visible(df_filtered["departamento"]))
            ]
            .groupby("departamento")["ocid"]
            .nunique()
            .reset_index(name="procesos")
            .sort_values("procesos", ascending=False)
            .head(15)
        )

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=g7, x="procesos", y="departamento", color="darkorange", ax=ax)
        ax.set_title("Top 15 departamentos con un solo postor")
        ax.set_xlabel("Procesos")
        ax.set_ylabel("Departamento")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.write("Distribución de postores por categoría")

        g8 = df_filtered[df_filtered["n_postores"] > 0].copy()

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=g8, x="categoria", y="n_postores", showfliers=False, ax=ax)
        ax.set_title("Distribución de postores por categoría")
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Número de postores")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


# ============================================================
# 11. SECCION: RIESGO ECONOMICO
# ============================================================

elif opciones == "Riesgo económico":
    col1, col2 = st.columns(2)

    with col1:
        st.write("Monto en riesgo frente a monto competitivo por año")

        g9 = (
            df_filtered.groupby("año", as_index=False)
            .agg(
                monto_total=("monto_adjudicado", "sum"),
                monto_riesgo=("monto_adjudicado", lambda s: s[df_filtered.loc[s.index, "un_solo_postor"]].sum()),
            )
        )

        g9["monto_competitivo"] = g9["monto_total"] - g9["monto_riesgo"]
        g9[["monto_riesgo", "monto_competitivo"]] = (
            g9[["monto_riesgo", "monto_competitivo"]] / 1_000_000
        )

        # Este gráfico mantiene la misma estructura del notebook:
        # dos barras por año construidas con Matplotlib.
        x = np.arange(len(g9))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width / 2, g9["monto_riesgo"], width=width, label="Monto en riesgo")
        ax.bar(x + width / 2, g9["monto_competitivo"], width=width, label="Monto competitivo")
        ax.set_xticks(x)
        ax.set_xticklabels(g9["año"].astype(str))
        ax.set_title("Monto en riesgo frente a monto competitivo por año")
        ax.set_xlabel("Año")
        ax.set_ylabel("Millones de PEN")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.write("Evolución del gasto por categoría")

        g10 = (
            df_filtered.groupby(["año", "categoria"])["monto_MM"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            g10,
            x="año",
            y="monto_MM",
            color="categoria",
            markers=True,
            title="Evolución del gasto por categoría",
            labels={"año": "Año", "monto_MM": "Millones de PEN", "categoria": "Categoría"},
            color_discrete_map={"Bienes": "#636efa", "Obras": "#EF553B", "Servicios": "#00cc96"},
        )

        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.write("Top 15 entidades con más contrataciones directas")

        g11 = (
            df_filtered[
                (df_filtered["directa"] == True)
                & (es_valor_visible(df_filtered["entidad_compradora"]))
            ]
            .groupby("entidad_compradora")["ocid"]
            .nunique()
            .reset_index(name="procesos")
            .sort_values("procesos", ascending=False)
            .head(15)
        )

        fig, ax = plt.subplots(figsize=(8, 6))
        g11_plot = g11.set_index("entidad_compradora")["procesos"].sort_values()
        g11_plot.plot(kind="barh", color="slateblue", ax=ax)
        ax.set_title("Top 15 entidades con más contrataciones directas")
        ax.set_xlabel("Procesos directos")
        ax.set_ylabel("Entidad compradora")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.write("Monto adjudicado frente a número de postores")

        g12 = df_filtered[
            ["ocid", "n_postores", "monto_adjudicado", "un_solo_postor", "categoria", "departamento"]
        ].dropna().copy()

        fig = px.scatter(
            g12,
            x="n_postores",
            y="monto_adjudicado",
            color="un_solo_postor",
            title="Monto adjudicado frente a número de postores",
            labels={"n_postores": "Número de postores", "monto_adjudicado": "Monto adjudicado (PEN)"},
            opacity=0.5,
            color_discrete_map={False: "#636EFA", True: "#EF553B"},
        )

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 12. SECCION: TRANSPARENCIA GEOGRAFICA
# ============================================================

elif opciones == "Transparencia geográfica":
    col1, col2 = st.columns([1, 1.35])

    with col1:
        st.write("Riesgo por departamento y categoría")

        top_dptos = (
            df_filtered[es_valor_visible(df_filtered["departamento"])]
            .groupby("departamento")["ocid"]
            .nunique()
            .sort_values(ascending=False)
            .head(15)
            .index
        )

        g13 = (
            df_filtered[
                df_filtered["departamento"].isin(top_dptos)
                & es_valor_visible(df_filtered["categoria"])
            ]
            .groupby(["departamento", "categoria"])["un_solo_postor"]
            .mean()
            .mul(100)
            .reset_index()
        )

        g13_heat = (
            g13.pivot(index="departamento", columns="categoria", values="un_solo_postor")
            .fillna(0)
        )
        fig, ax = plt.subplots(figsize=(11, 8))
        sns.heatmap(g13_heat, cmap="YlOrRd", annot=True, fmt=".1f", ax=ax)
        ax.set_title("Riesgo por departamento y categoría (%)")
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Departamento")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.write("Evolución mensual de directas frente a competitivas")

        g14 = (
            df_filtered[
                df_filtered["metodo_simple"].isin(["Competitivo", "Directa"])
                & df_filtered["mes_reporte"].notna()
            ]
            .groupby(["mes_reporte", "metodo_simple"])["ocid"]
            .nunique()
            .reset_index(name="procesos")
            .sort_values("mes_reporte")
        )

        # Convertimos el periodo mensual a fecha para que el eje X
        # quede legible y no imprima todos los meses como texto.
        g14["mes_reporte"] = pd.to_datetime(g14["mes_reporte"], errors="coerce")
        g14 = g14.dropna(subset=["mes_reporte"]).sort_values("mes_reporte")

        fig, ax = plt.subplots(figsize=(14, 6))
        sns.lineplot(
            data=g14,
            x="mes_reporte",
            y="procesos",
            hue="metodo_simple",
            marker="o",
            hue_order=["Competitivo", "Directa"],
            ax=ax,
        )
        ax.set_title("Evolución mensual de contrataciones directas y competitivas")
        ax.set_xlabel("Periodo mensual del reporte")
        ax.set_ylabel("Procesos")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.grid(True, alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.write("Top 15 proveedores ganadores repetidos")

        g15 = (
            df_filtered[es_valor_visible(df_filtered["proveedor_ganador"])]
            .groupby("proveedor_ganador")["ocid"]
            .nunique()
            .reset_index(name="procesos_ganados")
            .sort_values("procesos_ganados", ascending=False)
            .head(15)
        )

        fig, ax = plt.subplots(figsize=(8, 6))
        g15_plot = g15.set_index("proveedor_ganador")["procesos_ganados"].sort_values()
        g15_plot.plot(kind="barh", color="teal", ax=ax)
        ax.set_title("Top 15 proveedores ganadores repetidos")
        ax.set_xlabel("Procesos adjudicados")
        ax.set_ylabel("Proveedor ganador")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col4:
        st.write("Score de transparencia por departamento")

        g16 = (
            df_filtered[es_valor_visible(df_filtered["departamento"])]
            .groupby("departamento", as_index=False)
            .agg(
                pct_directa=("directa", "mean"),
                pct_un_solo_postor=("un_solo_postor", "mean"),
                monto_total=("monto_adjudicado", "sum"),
                monto_riesgo=("monto_adjudicado", lambda s: s[df_filtered.loc[s.index, "un_solo_postor"]].sum()),
            )
        )

        g16["pct_directa"] = g16["pct_directa"] * 100
        g16["pct_un_solo_postor"] = g16["pct_un_solo_postor"] * 100
        g16["pct_monto_riesgo"] = np.where(
            g16["monto_total"] > 0,
            (g16["monto_riesgo"] / g16["monto_total"]) * 100,
            0,
        )

        g16["score_transparencia"] = 100 - (
            (g16["pct_directa"] + g16["pct_un_solo_postor"] + g16["pct_monto_riesgo"]) / 3
        )

        g16 = g16.sort_values("score_transparencia", ascending=False).head(15)
        g16 = g16.sort_values("score_transparencia", ascending=True)

        fig = px.bar(
            g16,
            x="score_transparencia",
            y="departamento",
            orientation="h",
            text="score_transparencia",
            title="Score de transparencia por departamento",
            labels={"score_transparencia": "Score de transparencia", "departamento": "Departamento"},
            color="score_transparencia",
            color_continuous_scale=["#2b3350", "#6ea8fe", "#ff6658"],
        )

        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
