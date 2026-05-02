from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# Configuramos la pagina antes de dibujar cualquier componente.
st.set_page_config(
    page_title="Dashboard de Contrataciones del Perú",
    page_icon="📊",
    layout="wide",
)

# Definimos las rutas principales del proyecto.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "contrataciones_peru_2022_2024_maestro.csv"


def aplicar_estilos() -> None:
    """Aplica un estilo oscuro para que el dashboard se vea como tablero ejecutivo."""
    st.markdown(
        """
        <style>
        :root {
            --bg-main: #0f1119;
            --bg-panel: #171b27;
            --bg-card: #1d2232;
            --bg-soft: #252c3f;
            --line: rgba(255,255,255,0.08);
            --text-main: #f5f7fb;
            --text-soft: #b8bfd1;
            --accent: #ff6658;
            --accent-2: #61d6a3;
            --accent-3: #6ea8fe;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255,102,88,0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(97,214,163,0.07), transparent 24%),
                linear-gradient(180deg, #0b0d14 0%, #111522 100%);
            color: var(--text-main);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111420 0%, #0d1018 100%);
            border-right: 1px solid var(--line);
        }

        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(32,38,54,0.98) 0%, rgba(24,29,41,0.98) 100%);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
            min-height: 120px;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--text-soft);
            font-size: 0.88rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text-main);
            font-size: 2rem;
        }

        .hero-box {
            background: linear-gradient(135deg, rgba(255,102,88,0.14), rgba(110,168,254,0.08));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 22px 24px;
            margin-bottom: 1rem;
        }

        .hero-top {
            color: #ffb3a8;
            font-size: 0.78rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }

        .hero-title {
            color: var(--text-main);
            font-size: 2rem;
            font-weight: 700;
            margin-top: 0.35rem;
            margin-bottom: 0.4rem;
        }

        .hero-subtitle {
            color: var(--text-soft);
            font-size: 0.98rem;
            line-height: 1.5;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 14px;
        }

        .badge-chip {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            color: var(--text-main);
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 0.82rem;
        }

        .section-note {
            color: var(--text-soft);
            font-size: 0.95rem;
            margin-top: -0.2rem;
            margin-bottom: 1rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.7rem;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 0.45rem;
        }

        .stTabs [data-baseweb="tab"] {
            background: #1b2030;
            border-radius: 12px;
            color: var(--text-soft);
            min-height: 54px;
            padding-left: 18px;
            padding-right: 18px;
            border: 1px solid rgba(255,255,255,0.04);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, rgba(255,102,88,0.95), rgba(255,126,93,0.9));
            color: white;
        }

        .chart-card {
            background: linear-gradient(180deg, rgba(24,29,41,0.97) 0%, rgba(18,22,32,0.97) 100%);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.7rem 0.7rem 0.25rem 0.7rem;
            margin-bottom: 1rem;
            box-shadow: 0 14px 32px rgba(0,0,0,0.18);
        }

        .chart-caption {
            color: var(--text-soft);
            font-size: 0.85rem;
            margin: 0.3rem 0 0.8rem 0.3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Lee la base maestra y prepara columnas utiles para el dashboard."""
    df = pd.read_csv(DATA_FILE, low_memory=False)

    # Convertimos columnas numericas para evitar errores en graficos y KPIs.
    df["n_postores"] = pd.to_numeric(df["n_postores"], errors="coerce")
    df["monto_adjudicado"] = pd.to_numeric(df["monto_adjudicado"], errors="coerce").fillna(0)
    df["monto_MM"] = df["monto_adjudicado"] / 1_000_000

    # Estandarizamos el indicador booleano.
    df["un_solo_postor"] = df["un_solo_postor"].astype(str).str.lower().eq("true")

    # Preparamos columnas de fecha para graficos temporales.
    df["fecha_proceso"] = pd.to_datetime(df["fecha_proceso"], errors="coerce")
    df["mes"] = df["fecha_proceso"].dt.to_period("M").astype(str)

    # Si la base conserva la columna original sin tilde, se renombra para unificar la presentación.
    if "anio" in df.columns and "año" not in df.columns:
        df = df.rename(columns={"anio": "año"})

    # Rellenamos textos para que filtros y etiquetas no queden vacios.
    for col in ["categoria", "metodo_simple", "departamento", "entidad_compradora", "proveedor_ganador"]:
        if col in df.columns:
            df[col] = df[col].fillna("Sin dato")

    return df


@st.cache_data
def cargar_proveedores() -> pd.DataFrame:
    """Carga una tabla auxiliar de proveedores ganadores para el ranking final."""
    partes = []
    for año in [2022, 2023, 2024]:
        ruta = DATA_DIR / str(año) / "awards_suppliers.csv"
        temp = pd.read_csv(ruta, usecols=["main_ocid", "name"], low_memory=False)
        temp["año"] = año
        partes.append(temp)

    proveedores = pd.concat(partes, ignore_index=True)
    proveedores = proveedores.rename(columns={"main_ocid": "ocid", "name": "proveedor_ganador"})
    proveedores["proveedor_ganador"] = proveedores["proveedor_ganador"].fillna("Sin dato")
    return proveedores


def formatear_entero(valor: float) -> str:
    """Formatea un entero para mostrarlo con separadores de miles."""
    return f"{int(valor):,}"


def formatear_mm(valor: float) -> str:
    """Formatea montos expresados en millones de soles."""
    return f"{valor:,.2f}"


def tema_plotly(fig, titulo: str):
    """Aplica un estilo visual uniforme a todos los graficos de Plotly."""
    fig.update_layout(
        title=titulo,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#171b27",
        font=dict(color="#f5f7fb"),
        title_font=dict(size=20, color="#f5f7fb"),
        margin=dict(l=30, r=30, t=60, b=30),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.08)",
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.08)",
    )
    return fig


def tarjeta_grafico(titulo: str, descripcion: str) -> None:
    """Dibuja el encabezado corto de cada bloque visual."""
    st.markdown(
        f"""
        <div class="chart-card">
            <div style="font-size:1.05rem; font-weight:700; color:#f5f7fb; margin:0.2rem 0 0 0.3rem;">{titulo}</div>
            <div class="chart-caption">{descripcion}</div>
        """,
        unsafe_allow_html=True,
    )


def cerrar_tarjeta() -> None:
    """Cierra el contenedor HTML de la tarjeta visual."""
    st.markdown("</div>", unsafe_allow_html=True)


def obtener_score_departamento(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Calcula un score simple de transparencia por departamento."""
    score = (
        dataframe[dataframe["departamento"] != "Sin dato"]
        .groupby("departamento", as_index=False)
        .agg(
            procesos=("ocid", "nunique"),
            pct_directa=("metodo_simple", lambda s: (s == "Directa").mean() * 100),
            pct_un_solo_postor=("un_solo_postor", "mean"),
            monto_total=("monto_adjudicado", "sum"),
            monto_riesgo=("monto_adjudicado", lambda s: s[dataframe.loc[s.index, "un_solo_postor"]].sum()),
        )
    )
    score["pct_un_solo_postor"] = score["pct_un_solo_postor"] * 100
    score["pct_monto_riesgo"] = np.where(
        score["monto_total"] > 0,
        100 * score["monto_riesgo"] / score["monto_total"],
        0,
    )
    score["score_transparencia"] = 100 - (
        score["pct_directa"] + score["pct_un_solo_postor"] + score["pct_monto_riesgo"]
    ) / 3
    return score


aplicar_estilos()
df = cargar_datos()
proveedores = cargar_proveedores()

# Preparamos la barra lateral con filtros globales.
with st.sidebar:
    st.markdown("## 📁 Dashboard OECE")
    st.caption("Filtros globales del análisis")

    años = sorted(df["año"].dropna().unique().tolist())
    departamentos = sorted(df["departamento"].dropna().unique().tolist())
    categorias = sorted(df["categoria"].dropna().unique().tolist())

    filtro_años = st.multiselect("Año", options=años, default=años)
    filtro_departamentos = st.multiselect("Departamento", options=departamentos)
    filtro_categorias = st.multiselect("Categoría", options=categorias)

    st.markdown("---")
    st.caption(
        "Para recuperar la vista general del análisis, deje sin seleccionar los filtros de Departamento y Categoría."
    )


# Aplicamos los filtros al DataFrame principal.
dash = df.copy()
if filtro_años:
    dash = dash[dash["año"].isin(filtro_años)]
if filtro_departamentos:
    dash = dash[dash["departamento"].isin(filtro_departamentos)]
if filtro_categorias:
    dash = dash[dash["categoria"].isin(filtro_categorias)]

# Esta tabla auxiliar solo deja proveedores asociados a la vista filtrada.
proveedores_dash = proveedores.merge(dash[["ocid"]].drop_duplicates(), on="ocid", how="inner")

if dash.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# Calculamos indicadores generales del tablero.
total_procesos = dash["ocid"].nunique()
pct_un_postor = dash["un_solo_postor"].mean() * 100
monto_total = dash["monto_MM"].sum()
pct_directa = (dash["metodo_simple"] == "Directa").mean() * 100
monto_riesgo = dash.loc[dash["un_solo_postor"], "monto_MM"].sum()
departamentos_activos = dash.loc[dash["departamento"] != "Sin dato", "departamento"].nunique()

# Cabecera principal, mas cercana a un tablero ejecutivo.
st.markdown(
    f"""
    <div class="hero-box">
        <div class="hero-top">Proyecto Final · Dashboard de Contrataciones Públicas</div>
        <div class="hero-title">Transparencia y Competencia en Compras del Estado Peruano</div>
        <div class="hero-subtitle">
            Este tablero sintetiza los procesos de contratación pública correspondientes a los años 2022, 2023 y 2024.
            La exposición se organiza en cuatro secciones: resumen general, competencia,
            riesgo económico y transparencia geográfica.
        </div>
        <div class="badge-row">
            <span class="badge-chip">Procesos filtrados: {formatear_entero(total_procesos)}</span>
            <span class="badge-chip">Monto total: S/ {formatear_mm(monto_total)} MM</span>
            <span class="badge-chip">% con un solo postor: {pct_un_postor:.2f}%</span>
            <span class="badge-chip">Departamentos visibles: {formatear_entero(departamentos_activos)}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tarjetas KPI de alto nivel.
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Procesos analizados", formatear_entero(total_procesos))
col2.metric("% un solo postor", f"{pct_un_postor:.2f}%")
col3.metric("Monto total MM PEN", formatear_mm(monto_total))
col4.metric("% contratación directa", f"{pct_directa:.2f}%")
col5.metric("Monto en riesgo MM", formatear_mm(monto_riesgo))

st.markdown(
    '<div class="section-note">Cada pestaña desarrolla una dimensión específica del análisis y organiza la exposición de resultados ante el jurado.</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📘 Resumen", "👥 Competencia", "💰 Riesgo Económico", "🗺️ Transparencia Geográfica"]
)

with tab1:
    st.subheader("Sección 1. Resumen General")
    st.caption("La primera sección presenta la dimensión del universo analizado, la composición del gasto y la estructura general del sistema observado.")

    c1, c2 = st.columns([1.2, 1.8])

    with c1:
        tarjeta_grafico(
            "Lectura rápida del período",
            "Estas tarjetas sintetizan el contexto general del análisis antes de revisar el detalle de los gráficos.",
        )
        mini1, mini2 = st.columns(2)
        mini1.metric("Años visibles", formatear_entero(dash["año"].nunique()))
        mini2.metric("Categorías", formatear_entero(dash["categoria"].nunique()))
        mini3, mini4 = st.columns(2)
        mini3.metric("Entidades", formatear_entero(dash["entidad_compradora"].nunique()))
        mini4.metric("Proveedores", formatear_entero(proveedores_dash["proveedor_ganador"].nunique()))
        cerrar_tarjeta()

    with c2:
        tarjeta_grafico(
            "Distribución del monto por categoría",
            "El gráfico identifica en qué categoría se concentra el monto adjudicado dentro del período analizado.",
        )
        g1 = dash.groupby("categoria", as_index=False).agg(monto_MM=("monto_MM", "sum"))
        fig1 = px.treemap(
            g1,
            path=["categoria"],
            values="monto_MM",
            color="monto_MM",
            color_continuous_scale=["#2b3350", "#3a5ccf", "#ff6658"],
        )
        tema_plotly(fig1, "Monto adjudicado por categoría")
        st.plotly_chart(fig1, use_container_width=True)
        cerrar_tarjeta()

    c3, c4 = st.columns(2)

    with c3:
        tarjeta_grafico(
            "Procesos por año",
            "La serie permite comparar la magnitud de procesos registrados en cada año del período.",
        )
        g2 = dash.groupby("año", as_index=False).agg(procesos=("ocid", "nunique"))
        fig2 = px.bar(
            g2,
            x="año",
            y="procesos",
            text="procesos",
            color="procesos",
            color_continuous_scale=["#203354", "#4d7cff", "#8cc8ff"],
        )
        fig2.update_traces(textposition="outside")
        tema_plotly(fig2, "Cantidad de procesos por año")
        st.plotly_chart(fig2, use_container_width=True)
        cerrar_tarjeta()

    with c4:
        tarjeta_grafico(
            "Participación por método",
            "La composición porcentual permite distinguir el peso relativo de cada modalidad de contratación.",
        )
        g3 = dash.groupby("metodo_simple", as_index=False).agg(procesos=("ocid", "nunique"))
        fig3 = px.pie(
            g3,
            names="metodo_simple",
            values="procesos",
            hole=0.55,
            color="metodo_simple",
            color_discrete_map={
                "Competitivo": "#61d6a3",
                "Directa": "#ff6658",
                "Selectivo": "#6ea8fe",
                "Sin dato": "#8b93a8",
            },
        )
        tema_plotly(fig3, "Participación de procesos por método")
        st.plotly_chart(fig3, use_container_width=True)
        cerrar_tarjeta()

with tab2:
    st.subheader("Sección 2. Competencia")
    st.caption("La segunda sección examina la intensidad competitiva de los procesos y la localización de señales de menor concurrencia.")

    c1, c2 = st.columns(2)

    with c1:
        tarjeta_grafico(
            "Distribución del número de postores",
            "La distribución muestra si predomina una participación reducida o una concurrencia más amplia entre postores.",
        )
        g4 = dash["n_postores"].dropna().clip(upper=10)
        fig4 = px.histogram(g4, nbins=10, color_discrete_sequence=["#6ea8fe"])
        tema_plotly(fig4, "Número de postores por proceso")
        fig4.update_xaxes(title="Número de postores (10 representa 10 o más)")
        fig4.update_yaxes(title="Cantidad de procesos")
        st.plotly_chart(fig4, use_container_width=True)
        cerrar_tarjeta()

    with c2:
        tarjeta_grafico(
            "Top departamentos con un solo postor",
            "El ranking territorial evidencia dónde se concentra la mayor cantidad de procesos con un único postor.",
        )
        g5 = (
            dash[dash["departamento"] != "Sin dato"]
            .groupby("departamento", as_index=False)
            .agg(casos_un_postor=("un_solo_postor", "sum"))
            .sort_values("casos_un_postor", ascending=False)
            .head(15)
        )
        fig5 = px.bar(
            g5,
            x="casos_un_postor",
            y="departamento",
            orientation="h",
            color="casos_un_postor",
            color_continuous_scale=["#4b1f22", "#ff6658", "#ffae8d"],
        )
        fig5.update_yaxes(categoryorder="total ascending")
        tema_plotly(fig5, "Departamentos con más casos de un solo postor")
        st.plotly_chart(fig5, use_container_width=True)
        cerrar_tarjeta()

    c3, c4 = st.columns(2)

    with c3:
        tarjeta_grafico(
            "Método por categoría",
            "La comparación permite identificar qué categorías se apoyan más en contratación directa y cuáles muestran mayor competencia.",
        )
        g6 = pd.crosstab(dash["categoria"], dash["metodo_simple"], normalize="index").reset_index()
        g6 = g6.melt(id_vars="categoria", var_name="metodo_simple", value_name="porcentaje")
        g6["porcentaje"] = g6["porcentaje"] * 100
        fig6 = px.bar(
            g6,
            x="categoria",
            y="porcentaje",
            color="metodo_simple",
            barmode="stack",
            color_discrete_map={
                "Competitivo": "#61d6a3",
                "Directa": "#ff6658",
                "Selectivo": "#6ea8fe",
                "Sin dato": "#8b93a8",
            },
        )
        tema_plotly(fig6, "Composición del método de contratación por categoría")
        fig6.update_yaxes(title="% dentro de cada categoría")
        st.plotly_chart(fig6, use_container_width=True)
        cerrar_tarjeta()

    with c4:
        tarjeta_grafico(
            "Caja de postores por categoría",
            "El diagrama resume mediana, dispersión y valores extremos de la competencia observada en cada categoría.",
        )
        g7 = dash[dash["n_postores"].notna()].copy()
        g7["n_postores"] = g7["n_postores"].clip(upper=15)
        fig7 = px.box(
            g7,
            x="categoria",
            y="n_postores",
            points=False,
            color="categoria",
            color_discrete_sequence=["#61d6a3", "#6ea8fe", "#ff6658"],
        )
        tema_plotly(fig7, "Distribución de postores por categoría")
        st.plotly_chart(fig7, use_container_width=True)
        cerrar_tarjeta()

with tab3:
    st.subheader("Sección 3. Riesgo Económico")
    st.caption("La tercera sección traduce las señales de competencia en montos, con el fin de estimar la exposición económica asociada al riesgo.")

    c1, c2 = st.columns(2)

    with c1:
        tarjeta_grafico(
            "Monto en riesgo vs monto competitivo",
            "La separación entre gasto en riesgo y gasto competitivo permite cuantificar la exposición económica vinculada a baja competencia.",
        )
        g8 = dash.groupby("año", as_index=False).agg(
            monto_total=("monto_adjudicado", "sum"),
            monto_riesgo=("monto_adjudicado", lambda s: s[dash.loc[s.index, "un_solo_postor"]].sum()),
        )
        g8["monto_competitivo"] = g8["monto_total"] - g8["monto_riesgo"]
        g8["monto_riesgo_mm"] = g8["monto_riesgo"] / 1_000_000
        g8["monto_competitivo_mm"] = g8["monto_competitivo"] / 1_000_000
        g8_plot = g8.melt(
            id_vars="año",
            value_vars=["monto_riesgo_mm", "monto_competitivo_mm"],
            var_name="tipo_monto",
            value_name="monto_mm",
        )
        fig8 = px.bar(
            g8_plot,
            x="año",
            y="monto_mm",
            color="tipo_monto",
            barmode="group",
            color_discrete_map={
                "monto_riesgo_mm": "#ff6658",
                "monto_competitivo_mm": "#61d6a3",
            },
        )
        tema_plotly(fig8, "Monto en riesgo frente a monto competitivo")
        st.plotly_chart(fig8, use_container_width=True)
        cerrar_tarjeta()

    with c2:
        tarjeta_grafico(
            "Evolución anual del gasto por categoría",
            "La evolución anual del gasto permite identificar cambios en la prioridad relativa de cada categoría de compra.",
        )
        g9 = dash.groupby(["año", "categoria"], as_index=False).agg(monto_MM=("monto_MM", "sum"))
        fig9 = px.line(
            g9,
            x="año",
            y="monto_MM",
            color="categoria",
            markers=True,
            color_discrete_map={
                "Bienes": "#61d6a3",
                "Servicios": "#6ea8fe",
                "Obras": "#ff6658",
                "Sin dato": "#8b93a8",
            },
        )
        tema_plotly(fig9, "Evolución del gasto por categoría")
        st.plotly_chart(fig9, use_container_width=True)
        cerrar_tarjeta()

    c3, c4 = st.columns(2)

    with c3:
        tarjeta_grafico(
            "Entidades con más contrataciones directas",
            "El ranking institucional destaca las entidades que concentran mayor número de procesos directos en la selección aplicada.",
        )
        g10 = (
            dash[dash["metodo_simple"] == "Directa"]
            .groupby("entidad_compradora", as_index=False)
            .agg(n_directas=("ocid", "nunique"))
            .sort_values("n_directas", ascending=False)
            .head(15)
        )
        fig10 = px.bar(
            g10,
            x="n_directas",
            y="entidad_compradora",
            orientation="h",
            color="n_directas",
            color_continuous_scale=["#1d3a2b", "#61d6a3", "#9bf3cb"],
        )
        fig10.update_yaxes(categoryorder="total ascending")
        tema_plotly(fig10, "Top entidades con más contratación directa")
        st.plotly_chart(fig10, use_container_width=True)
        cerrar_tarjeta()

    with c4:
        tarjeta_grafico(
            "Monto adjudicado vs número de postores",
            "La nube de puntos permite observar si los procesos de mayor monto coinciden con menores niveles de competencia.",
        )
        g11 = dash[(dash["monto_adjudicado"] > 0) & (dash["n_postores"].notna())].copy()
        if len(g11) > 5000:
            g11 = g11.sample(5000, random_state=42)
        fig11 = px.scatter(
            g11,
            x="n_postores",
            y="monto_adjudicado",
            color="un_solo_postor",
            hover_data=["ocid", "categoria", "departamento"],
            color_discrete_map={True: "#ff6658", False: "#61d6a3"},
        )
        tema_plotly(fig11, "Monto adjudicado y competencia")
        st.plotly_chart(fig11, use_container_width=True)
        cerrar_tarjeta()

with tab4:
    st.subheader("Sección 4. Transparencia Geográfica")
    st.caption("La cuarta sección traslada el análisis al territorio y muestra la distribución espacial de los principales indicadores de riesgo.")

    c1, c2 = st.columns(2)

    with c1:
        tarjeta_grafico(
            "Mapa de calor por departamento y categoría",
            "La intensidad del color representa un mayor porcentaje de procesos con un solo postor en la combinación analizada.",
        )
        top_dptos = (
            dash[dash["departamento"] != "Sin dato"]
            .groupby("departamento")["ocid"]
            .nunique()
            .sort_values(ascending=False)
            .head(15)
            .index
        )
        heat = (
            dash[dash["departamento"].isin(top_dptos)]
            .groupby(["departamento", "categoria"])["un_solo_postor"]
            .mean()
            .mul(100)
            .reset_index()
            .pivot(index="departamento", columns="categoria", values="un_solo_postor")
            .fillna(0)
        )
        fig12 = px.imshow(
            heat,
            text_auto=".1f",
            color_continuous_scale=["#1a1f2d", "#6f2630", "#ff6658"],
            aspect="auto",
        )
        tema_plotly(fig12, "Riesgo territorial por categoría")
        st.plotly_chart(fig12, use_container_width=True)
        cerrar_tarjeta()

    with c2:
        tarjeta_grafico(
            "Evolución mensual de directas vs competitivas",
            "La tendencia mensual permite observar la trayectoria comparada entre procesos directos y procesos competitivos.",
        )
        g12 = (
            dash[dash["metodo_simple"].isin(["Competitivo", "Directa"])]
            .groupby(["mes", "metodo_simple"], as_index=False)
            .agg(procesos=("ocid", "nunique"))
        )
        if not g12.empty:
            g12["mes_dt"] = pd.to_datetime(g12["mes"] + "-01")
            g12 = g12.sort_values("mes_dt")
            fig13 = px.line(
                g12,
                x="mes_dt",
                y="procesos",
                color="metodo_simple",
                markers=True,
                color_discrete_map={"Competitivo": "#61d6a3", "Directa": "#ff6658"},
            )
            tema_plotly(fig13, "Tendencia mensual por método")
            st.plotly_chart(fig13, use_container_width=True)
        cerrar_tarjeta()

    c3, c4 = st.columns(2)

    with c3:
        tarjeta_grafico(
            "Top proveedores ganadores repetidos",
            "El ranking resume el grado de concentración de adjudicaciones en un conjunto reducido de proveedores.",
        )
        g13 = (
            proveedores_dash.groupby("proveedor_ganador", as_index=False)
            .agg(procesos_ganados=("ocid", "nunique"))
            .sort_values("procesos_ganados", ascending=False)
            .head(15)
        )
        fig14 = px.bar(
            g13,
            x="procesos_ganados",
            y="proveedor_ganador",
            orientation="h",
            color="procesos_ganados",
            color_continuous_scale=["#321c1c", "#ff6658", "#ffb19c"],
        )
        fig14.update_yaxes(categoryorder="total ascending")
        tema_plotly(fig14, "Proveedores con más procesos ganados")
        st.plotly_chart(fig14, use_container_width=True)
        cerrar_tarjeta()

    with c4:
        tarjeta_grafico(
            "Score de transparencia por departamento",
            "La tabla consolida tres señales de interés: contratación directa, presencia de un solo postor y peso relativo del monto en riesgo.",
        )
        score = obtener_score_departamento(dash).sort_values("score_transparencia").head(15)
        st.dataframe(
            score[
                [
                    "departamento",
                    "procesos",
                    "pct_directa",
                    "pct_un_solo_postor",
                    "pct_monto_riesgo",
                    "score_transparencia",
                ]
            ].round(2),
            use_container_width=True,
            hide_index=True,
        )
        cerrar_tarjeta()
