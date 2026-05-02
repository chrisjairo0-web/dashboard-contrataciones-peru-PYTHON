# Dashboard de Contrataciones Públicas del Perú

Proyecto final desarrollado a partir de información OCDS correspondiente a los años `2022`, `2023` y `2024`.

## Descripción

El repositorio presenta un análisis de contrataciones públicas del Perú con énfasis en competencia, riesgo económico y transparencia territorial. El trabajo consolida los archivos originales, construye una base maestra única y organiza los resultados en visualizaciones y en un dashboard interactivo.

La exposición del proyecto sigue una secuencia ordenada:

1. Carga, integración y limpieza de datos.
1. Construcción de visualizaciones analíticas.
1. Cálculo de indicadores clave de transparencia.
1. Presentación final en un dashboard interactivo.

## Estructura del repositorio

1. `data/`
Contiene las carpetas `2022/`, `2023/` y `2024/` con los archivos CSV originales del conjunto de datos.

1. `data/contrataciones_peru_2022_2024_maestro.csv`
Corresponde a la base maestra consolidada, utilizada como fuente principal para indicadores, gráficos y dashboard.

1. `notebooks/01_carga_limpieza.ipynb`
Documenta la integración de los años, la revisión de la base maestra y la validación de las variables principales del proyecto.

1. `notebooks/02_visualizaciones.ipynb`
Presenta los `16` gráficos del informe, organizados en las cuatro secciones del proyecto: Resumen General, Competencia, Riesgo Económico y Transparencia Geográfica.

1. `notebooks/03_kpis_resumen.ipynb`
Resume los principales indicadores de transparencia y los organiza en una vista ejecutiva de apoyo para la sustentación.

1. `dashboard.py`
Contiene el script principal del dashboard interactivo desarrollado en Streamlit.

1. `requirements.txt`
Incluye las dependencias necesarias para reproducir el proyecto.

1. `README.md`
Describe la estructura del repositorio, el flujo de trabajo y la forma de ejecución.

## Librerías utilizadas

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `plotly`
- `streamlit`
- `pypdf`
- `ipython`
- `nbformat`

## Ejecución del proyecto

1. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

1. Revisar la integración y limpieza de datos:

Abrir `notebooks/01_carga_limpieza.ipynb`.

1. Revisar las visualizaciones del informe:

Abrir `notebooks/02_visualizaciones.ipynb`.

1. Revisar el resumen de indicadores:

Abrir `notebooks/03_kpis_resumen.ipynb`.

1. Ejecutar el dashboard interactivo:

```bash
streamlit run dashboard.py
```

## Resultados principales

El repositorio permite sustentar, entre otros resultados:

- volumen total de procesos analizados
- porcentaje de procesos con un solo postor
- monto adjudicado total
- distribución del gasto por categoría
- concentración territorial de procesos con menor competencia
- entidades con mayor presencia de contratación directa
- evolución temporal de procesos competitivos y directos

## Nota sobre los datos

Los archivos CSV originales tienen un tamaño considerable; por ello, el repositorio utiliza `Git LFS` para facilitar su almacenamiento y versionado en GitHub.

La versión final del proyecto trabaja con una salida principal en CSV, `contrataciones_peru_2022_2024_maestro.csv`, de modo que la trazabilidad del análisis pueda explicarse con claridad ante el jurado: primero se integran y depuran los datos, luego se calculan los indicadores y finalmente se presentan los resultados en gráficos y dashboard.
