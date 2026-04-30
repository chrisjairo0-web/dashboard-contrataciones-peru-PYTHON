# Dashboard de Contrataciones Publicas del Peru

Proyecto final del curso de Especializacion en Python.

## Descripcion

Este proyecto analiza las contrataciones publicas del Peru a partir de datos OCDS de los anios `2022`, `2023` y `2024`.
El objetivo es integrar los archivos originales, construir una base maestra y generar visualizaciones que ayuden a identificar patrones de riesgo, falta de competencia y concentracion de procesos.

El trabajo se organiza en tres partes principales:

- union y limpieza de datos
- visualizaciones del informe
- dashboard interactivo

## Estructura del repositorio

- `data/`
  Contiene las carpetas `2022/`, `2023/` y `2024/` con los CSVs originales del dataset.
- `data/contrataciones_peru_2022_2024_maestro.csv`
  Base maestra consolidada luego del proceso de union y limpieza.
- `notebooks/01_carga_limpieza.ipynb`
  Notebook que muestra como se cargan, unen y limpian los datos de los tres anios.
- `notebooks/02_visualizaciones.ipynb`
  Notebook con las visualizaciones organizadas en 4 secciones del proyecto:
  Resumen General, Competencia, Riesgo Economico y Transparencia Geografica.
- `notebooks/03_dashboard_rq.ipynb`
  Notebook tipo dashboard, inspirado en una vista de reporte interactivo aplicada al tema del proyecto.
- `dashboard.py`
  Dashboard interactivo en Streamlit.
- `requirements.txt`
  Archivo con las dependencias necesarias para ejecutar el proyecto.
- `.gitattributes`
  Configuracion de Git LFS para archivos grandes.
- `.gitignore`
  Exclusiones de archivos temporales y carpetas que no deben subirse al repositorio.

## Librerias utilizadas

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `plotly`
- `streamlit`
- `pypdf`

## Como ejecutar el proyecto

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Revisar la integracion y limpieza de datos:

Abrir `notebooks/01_carga_limpieza.ipynb`.

3. Revisar los graficos del informe:

Abrir `notebooks/02_visualizaciones.ipynb`.

4. Revisar la version de dashboard en notebook:

Abrir `notebooks/03_dashboard_rq.ipynb`.

5. Ejecutar el dashboard interactivo en Streamlit:

```bash
streamlit run dashboard.py
```

## Resultados esperados

Con este proyecto se pueden revisar, entre otros puntos:

- total de procesos analizados
- porcentaje de procesos con un solo postor
- monto adjudicado total
- distribucion del gasto por categoria
- departamentos con mayor concentracion de procesos de riesgo
- entidades con mayor numero de contrataciones directas
- evolucion temporal de procesos competitivos y directos

## Nota sobre los datos

Los archivos CSV originales son pesados, por lo que el repositorio usa `Git LFS` para poder almacenarlos correctamente en GitHub.

Ademas, la version final del proyecto mantiene una salida principal en CSV (`contrataciones_peru_2022_2024_maestro.csv`) para que el flujo sea mas simple y facil de explicar en la sustentacion.
