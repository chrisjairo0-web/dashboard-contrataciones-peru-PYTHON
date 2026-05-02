from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")

BASE = Path(__file__).resolve().parent
OUT = BASE / "report_assets"
OUT.mkdir(exist_ok=True)


def load_data() -> tuple[pd.DataFrame, str]:
    df = pd.read_csv(BASE / "data" / "contrataciones_peru_2022_2024_maestro.csv", low_memory=False)
    col_anio = "año" if "año" in df.columns else "anio"
    df["monto_adjudicado"] = pd.to_numeric(df["monto_adjudicado"], errors="coerce").fillna(0)
    df["monto_MM"] = pd.to_numeric(df["monto_MM"], errors="coerce").fillna(df["monto_adjudicado"] / 1_000_000)
    df["n_postores"] = pd.to_numeric(df["n_postores"], errors="coerce").fillna(0)
    df["un_solo_postor"] = df["un_solo_postor"].astype(str).str.lower().eq("true") | df["n_postores"].eq(1)
    df["directa"] = df["metodo_simple"].astype(str).str.contains("direct", case=False, na=False)
    df["fecha_proceso"] = pd.to_datetime(df["fecha_proceso"], errors="coerce")
    df["mes_dt"] = df["fecha_proceso"].dt.to_period("M").dt.to_timestamp()
    return df, col_anio


def save_current(fig_name: str, title: str, section: str, columns_used: str, description: str, meta: list[dict]) -> None:
    path = OUT / f"{fig_name}.png"
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    meta.append(
        {
            "archivo": path.name,
            "grafico": title,
            "seccion": section,
            "columnas": columns_used,
            "descripcion": description,
        }
    )


def flow_diagram(path: Path, title: str, boxes: dict, arrows: list[tuple[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.text(0.3, 7.6, title, fontsize=18, weight="bold", color="#1f3a5f")
    for _, (x, y, w, h, text) in boxes.items():
        rect = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=2,
            edgecolor="#6ea8fe",
            facecolor="white",
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, wrap=True)
    for a, b in arrows:
        x1, y1, w1, h1, _ = boxes[a]
        x2, y2, w2, h2, _ = boxes[b]
        if abs(y1 - y2) > 1 and abs(x1 - x2) < 1:
            start = (x1 + w1 / 2, y1)
            end = (x2 + w2 / 2, y2 + h2)
        else:
            start = (x1 + w1, y1 + h1 / 2) if x1 < x2 else (x1, y1 + h1 / 2)
            end = (x2, y2 + h2 / 2) if x1 < x2 else (x2 + w2, y2 + h2 / 2)
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18, linewidth=2, color="#5B9BD5"))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    sns.set_theme(style="whitegrid")
    df, col_anio = load_data()
    meta: list[dict] = []

    plt.figure(figsize=(8, 5))
    df.groupby("categoria")["monto_MM"].sum().sort_values().plot(kind="barh", color="#4472C4")
    plt.title("Gráfico 1. Monto adjudicado por categoría")
    plt.xlabel("Millones de PEN")
    plt.ylabel("Categoría")
    save_current("grafico_01", "Monto adjudicado por categoría", "Resumen General", "categoria, monto_MM", "Identifica la categoría en la que se concentra el gasto adjudicado.", meta)

    plt.figure(figsize=(7, 5))
    g2 = df.groupby(col_anio, as_index=False).agg(procesos=("ocid", "nunique"))
    sns.barplot(data=g2, x=col_anio, y="procesos", color="#5B9BD5")
    plt.title("Gráfico 2. Cantidad de procesos por año")
    plt.xlabel("Año")
    plt.ylabel("Procesos")
    save_current("grafico_02", "Cantidad de procesos por año", "Resumen General", "ocid, año", "Compara la magnitud de procesos registrados en cada año.", meta)

    plt.figure(figsize=(6.5, 6.5))
    g3 = df.groupby("metodo_simple", as_index=False).agg(procesos=("ocid", "nunique"))
    plt.pie(g3["procesos"], labels=g3["metodo_simple"], autopct="%1.1f%%", startangle=90)
    plt.title("Gráfico 3. Participación de procesos por método")
    save_current("grafico_03", "Participación de procesos por método", "Resumen General", "metodo_simple, ocid", "Muestra la composición relativa de las modalidades de contratación.", meta)

    plt.figure(figsize=(8, 5))
    g4 = df.groupby([col_anio, "categoria"], as_index=False).agg(monto_MM=("monto_MM", "sum"))
    sns.barplot(data=g4, x=col_anio, y="monto_MM", hue="categoria")
    plt.title("Gráfico 4. Monto adjudicado por año y categoría")
    plt.xlabel("Año")
    plt.ylabel("Millones de PEN")
    save_current("grafico_04", "Monto adjudicado por año y categoría", "Resumen General", "año, categoria, monto_MM", "Permite observar la variación del gasto por categoría en cada período.", meta)

    plt.figure(figsize=(8, 5))
    plt.hist(df["n_postores"], bins=20, color="#ED7D31", edgecolor="black")
    plt.title("Gráfico 5. Distribución del número de postores")
    plt.xlabel("Número de postores")
    plt.ylabel("Frecuencia")
    save_current("grafico_05", "Distribución del número de postores", "Competencia", "n_postores", "Describe el comportamiento general de la concurrencia en los procesos.", meta)

    plt.figure(figsize=(7, 5))
    df.groupby(col_anio)["un_solo_postor"].mean().mul(100).plot(kind="bar", color="#C0504D")
    plt.title("Gráfico 6. Porcentaje de procesos con un solo postor por año")
    plt.xlabel("Año")
    plt.ylabel("Porcentaje")
    save_current("grafico_06", "Porcentaje de procesos con un solo postor por año", "Competencia", "año, un_solo_postor", "Resume la principal señal de baja competencia por período.", meta)

    plt.figure(figsize=(8, 6))
    g7 = (
        df[df["un_solo_postor"]]
        .groupby("departamento", as_index=False)
        .agg(procesos=("ocid", "nunique"))
        .sort_values("procesos", ascending=False)
        .head(15)
    )
    sns.barplot(data=g7, x="procesos", y="departamento", color="#F4B183")
    plt.title("Gráfico 7. Top 15 departamentos con un solo postor")
    plt.xlabel("Procesos")
    plt.ylabel("Departamento")
    save_current("grafico_07", "Top 15 departamentos con un solo postor", "Competencia", "departamento, ocid, un_solo_postor", "Localiza territorialmente la mayor concentración de procesos con baja competencia.", meta)

    plt.figure(figsize=(8, 5))
    g8 = df[df["n_postores"] > 0].copy()
    sns.boxplot(data=g8, x="categoria", y="n_postores", showfliers=False)
    plt.title("Gráfico 8. Distribución de postores por categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Número de postores")
    save_current("grafico_08", "Distribución de postores por categoría", "Competencia", "categoria, n_postores", "Compara el comportamiento competitivo típico entre categorías.", meta)

    plt.figure(figsize=(8, 5))
    g9 = df.groupby(col_anio, as_index=False).agg(
        monto_total=("monto_adjudicado", "sum"),
        monto_riesgo=("monto_adjudicado", lambda s: s[df.loc[s.index, "un_solo_postor"]].sum()),
    )
    g9["monto_competitivo"] = g9["monto_total"] - g9["monto_riesgo"]
    g9[["monto_riesgo", "monto_competitivo"]] /= 1_000_000
    x = np.arange(len(g9))
    w = 0.35
    plt.bar(x - w / 2, g9["monto_riesgo"], width=w, label="Monto en riesgo")
    plt.bar(x + w / 2, g9["monto_competitivo"], width=w, label="Monto competitivo")
    plt.xticks(x, g9[col_anio].astype(str))
    plt.title("Gráfico 9. Monto en riesgo frente a monto competitivo por año")
    plt.xlabel("Año")
    plt.ylabel("Millones de PEN")
    plt.legend()
    save_current("grafico_09", "Monto en riesgo frente a monto competitivo por año", "Riesgo Económico", "año, monto_adjudicado, un_solo_postor", "Separa la exposición económica según el nivel de competencia observado.", meta)

    plt.figure(figsize=(8, 5))
    g10 = df.groupby([col_anio, "categoria"], as_index=False).agg(monto_MM=("monto_MM", "sum"))
    sns.lineplot(data=g10, x=col_anio, y="monto_MM", hue="categoria", marker="o")
    plt.title("Gráfico 10. Evolución anual del gasto por categoría")
    plt.xlabel("Año")
    plt.ylabel("Millones de PEN")
    save_current("grafico_10", "Evolución anual del gasto por categoría", "Riesgo Económico", "año, categoria, monto_MM", "Muestra cambios en la importancia relativa de cada categoría de compra.", meta)

    plt.figure(figsize=(8, 6))
    (
        df[df["directa"]]
        .groupby("entidad_compradora", as_index=True)["ocid"]
        .nunique()
        .sort_values(ascending=False)
        .head(15)
        .sort_values()
        .plot(kind="barh", color="#70AD47")
    )
    plt.title("Gráfico 11. Top 15 entidades con más contrataciones directas")
    plt.xlabel("Procesos directos")
    plt.ylabel("Entidad compradora")
    save_current("grafico_11", "Top 15 entidades con más contrataciones directas", "Riesgo Económico", "entidad_compradora, metodo_simple, ocid", "Identifica concentración institucional de procedimientos directos.", meta)

    plt.figure(figsize=(8, 5))
    g12 = df[(df["monto_adjudicado"] > 0) & (df["n_postores"].notna())].copy()
    if len(g12) > 5000:
        g12 = g12.sample(5000, random_state=42)
    plt.scatter(g12["n_postores"], g12["monto_adjudicado"], c=np.where(g12["un_solo_postor"], "#C0504D", "#5B9BD5"), alpha=0.35)
    plt.title("Gráfico 12. Monto adjudicado frente a número de postores")
    plt.xlabel("Número de postores")
    plt.ylabel("Monto adjudicado (PEN)")
    save_current("grafico_12", "Monto adjudicado frente a número de postores", "Riesgo Económico", "n_postores, monto_adjudicado, un_solo_postor", "Contrasta dimensión económica y nivel de concurrencia.", meta)

    plt.figure(figsize=(10, 8))
    g13 = (
        df.groupby(["departamento", "categoria"])["un_solo_postor"]
        .mean()
        .mul(100)
        .reset_index()
        .pivot(index="departamento", columns="categoria", values="un_solo_postor")
        .fillna(0)
    )
    sns.heatmap(g13, cmap="YlOrRd", annot=True, fmt=".1f")
    plt.title("Gráfico 13. Riesgo por departamento y categoría (%)")
    plt.xlabel("Categoría")
    plt.ylabel("Departamento")
    save_current("grafico_13", "Riesgo por departamento y categoría (%)", "Transparencia Geográfica", "departamento, categoria, un_solo_postor", "Resume el porcentaje de procesos con un solo postor según territorio y categoría.", meta)

    plt.figure(figsize=(10, 5))
    g14 = df.dropna(subset=["mes_dt"]).groupby(["mes_dt", "directa"], as_index=False).agg(procesos=("ocid", "nunique"))
    sns.lineplot(data=g14, x="mes_dt", y="procesos", hue="directa", marker="o")
    plt.title("Gráfico 14. Evolución mensual de directas frente a competitivas")
    plt.xlabel("Mes")
    plt.ylabel("Procesos")
    save_current("grafico_14", "Evolución mensual de directas frente a competitivas", "Transparencia Geográfica", "mes, metodo_simple, ocid", "Permite observar la trayectoria temporal del método de contratación.", meta)

    plt.figure(figsize=(8, 6))
    (
        df.groupby("proveedor_ganador", as_index=True)["ocid"]
        .nunique()
        .sort_values(ascending=False)
        .head(15)
        .sort_values()
        .plot(kind="barh", color="#00B0F0")
    )
    plt.title("Gráfico 15. Top 15 proveedores ganadores repetidos")
    plt.xlabel("Procesos adjudicados")
    plt.ylabel("Proveedor ganador")
    save_current("grafico_15", "Top 15 proveedores ganadores repetidos", "Transparencia Geográfica", "proveedor_ganador, ocid", "Muestra la concentración de adjudicaciones en un grupo reducido de proveedores.", meta)

    plt.figure(figsize=(8, 6))
    g16 = df.groupby("departamento", as_index=False).agg(
        pct_directa=("directa", "mean"),
        pct_un_solo_postor=("un_solo_postor", "mean"),
        monto_total=("monto_adjudicado", "sum"),
        monto_riesgo=("monto_adjudicado", lambda s: s[df.loc[s.index, "un_solo_postor"]].sum()),
    )
    g16["pct_directa"] *= 100
    g16["pct_un_solo_postor"] *= 100
    g16["pct_monto_riesgo"] = np.where(g16["monto_total"] > 0, (g16["monto_riesgo"] / g16["monto_total"]) * 100, 0)
    g16["score_transparencia"] = 0.4 * g16["pct_directa"] + 0.3 * g16["pct_un_solo_postor"] + 0.3 * g16["pct_monto_riesgo"]
    g16 = g16.sort_values("score_transparencia", ascending=False).head(15).sort_values("score_transparencia")
    plt.barh(g16["departamento"], g16["score_transparencia"], color="#7030A0")
    plt.title("Gráfico 16. Score de transparencia por departamento")
    plt.xlabel("Score de transparencia")
    plt.ylabel("Departamento")
    save_current("grafico_16", "Score de transparencia por departamento", "Transparencia Geográfica", "departamento, directa, un_solo_postor, monto_adjudicado", "Sintetiza tres señales de interés en un único indicador territorial.", meta)

    boxes_asis = {
        "a": (0.5, 5.7, 2.4, 1.0, "Descarga manual de archivos CSV\nOCDS por año"),
        "b": (3.4, 5.7, 2.6, 1.0, "Apertura individual\nen Excel"),
        "c": (6.5, 5.7, 2.8, 1.0, "Cruce manual con\nVLOOKUP y tablas dinámicas"),
        "d": (9.9, 5.7, 2.6, 1.0, "Construcción manual\nde gráficos y reportes"),
        "e": (3.4, 3.5, 2.6, 1.0, "Validación manual\nde errores y vacíos"),
        "f": (6.5, 3.5, 2.8, 1.0, "Actualización periódica\nconsumidora de tiempo"),
        "g": (9.9, 3.5, 2.6, 1.0, "Análisis tardío\ny estático"),
    }
    flow_diagram(OUT / "flujo_asis.png", "Figura 1. Flujo actual de análisis manual (AS-IS)", boxes_asis, [("a", "b"), ("b", "c"), ("c", "d"), ("b", "e"), ("e", "f"), ("f", "g")])

    boxes_tobe = {
        "a": (0.4, 5.8, 2.5, 1.0, "Carga automática de\narchivos 2022, 2023 y 2024"),
        "b": (3.3, 5.8, 2.7, 1.0, "Integración por ocid\ny consolidación anual"),
        "c": (6.5, 5.8, 2.7, 1.0, "Limpieza y creación de\nvariables derivadas"),
        "d": (9.7, 5.8, 2.8, 1.0, "Base maestra única\nen CSV"),
        "e": (3.3, 3.5, 2.7, 1.0, "Cálculo automático\nde KPIs"),
        "f": (6.5, 3.5, 2.7, 1.0, "Generación de 16\nvisualizaciones"),
        "g": (9.7, 3.5, 2.8, 1.0, "Dashboard interactivo\nen Streamlit"),
        "h": (6.5, 1.2, 2.7, 1.0, "Exposición, análisis\ny priorización de riesgo"),
    }
    flow_diagram(OUT / "flujo_tobe.png", "Figura 2. Flujo propuesto con dashboard automatizado (TO-BE)", boxes_tobe, [("a", "b"), ("b", "c"), ("c", "d"), ("b", "e"), ("e", "f"), ("f", "g"), ("f", "h")])

    pd.DataFrame(meta).to_csv(OUT / "anexo_estructura_dashboard.csv", index=False, encoding="utf-8-sig")
    print("Assets generados en", OUT)
    print("Total gráficos:", len(meta))


if __name__ == "__main__":
    main()
