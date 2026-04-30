# Dashboard de Contrataciones Publicas del Peru

Proyecto final del curso de Especializacion en Python.

## Estructura

- `data/`
  Contiene las carpetas `2022/`, `2023/` y `2024/` con los CSVs originales del dataset OCDS.
- `data/contrataciones_peru_2022_2024_maestro.csv`
  Base maestra consolidada luego de la union y limpieza.
- `notebooks/01_carga_limpieza.ipynb`
  Carga, union y limpieza de los datos.
- `notebooks/02_visualizaciones.ipynb`
  Graficos organizados en 4 secciones analiticas.
- `notebooks/03_dashboard_rq.ipynb`
  Version tipo dashboard en notebook.
- `dashboard.py`
  Dashboard interactivo en Streamlit.
- `requirements.txt`
  Dependencias del proyecto.

## Como usar

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Revisar la union de datos:

Abrir `notebooks/01_carga_limpieza.ipynb`.

3. Revisar los graficos del informe:

Abrir `notebooks/02_visualizaciones.ipynb`.

4. Revisar el dashboard en notebook:

Abrir `notebooks/03_dashboard_rq.ipynb`.

5. Ejecutar el dashboard interactivo:

```bash
streamlit run dashboard.py
```

## Nota

En esta version final se deja solo la salida en CSV para mantener el proyecto mas simple y facil de explicar.
