# Análisis de datasets de ciberseguridad con Big Data

Proyecto integrador de análisis exploratorio y consulta de **61 datasets de ciberseguridad orientados a la detección de intrusiones**. Combina limpieza de datos con Python, procesamiento mediante Apache Spark, consultas documentales con MongoDB y un dashboard interactivo desarrollado en Streamlit.

## Objetivo

Organizar y analizar un catálogo de datasets de ciberseguridad para facilitar la selección de conjuntos de datos según sus características: año, fuentes de información (red y/o host), entorno, etiquetado, tamaño, tipos de ataques y citas recientes.

## Tecnologías utilizadas

- **Python:** procesamiento y análisis de datos.
- **Pandas y NumPy:** lectura, depuración y transformación del catálogo.
- **PySpark / Apache Spark:** consultas, agregaciones y análisis mediante DataFrames y Spark SQL.
- **MongoDB y PyMongo:** almacenamiento y consultas de documentos. Si no hay un servidor disponible, se utiliza **mongomock** como alternativa en memoria.
- **Matplotlib, Seaborn y Plotly:** visualización de resultados.
- **Streamlit:** dashboard interactivo con filtros y exportación.
- **Google Colab:** entorno previsto para ejecutar el notebook.

## Funcionalidades

### 1. Preparación y limpieza de datos

- Lectura de `datasets.csv`, separado por punto y coma (`;`).
- Eliminación de registros duplicados y espacios innecesarios.
- Normalización de valores faltantes y categorías.
- Conversión de años, citas y tamaños a valores numéricos.
- Clasificación de fuentes en **Solo red**, **Solo host**, **Red + Host** o **Ninguno**.
- Identificación de datasets etiquetados y de sistemas operativos.
- Cálculo de tamaño en GB, antigüedad y categorías de tamaño.
- Exportación del resultado a `datasets_limpio.csv`.

### 2. Procesamiento con Apache Spark

- Carga del catálogo procesado con PySpark.
- Filtrado de datasets recientes que incluyen datos de red y host.
- Agrupaciones por entorno y época.
- Análisis de citas y disponibilidad de etiquetas utilizando Spark SQL.
- Relación de tipos de datos con posibles aplicaciones: **SIEM/XDR**, **IDS/NetFlow** y **EDR**.

### 3. Consultas con MongoDB

- Inserción del catálogo limpio en la colección `ciberseguridad.datasets`.
- Búsqueda de datasets que cumplen criterios de fecha, etiquetado, fuentes de datos y tamaño.
- Consultas por entorno y sistema operativo.
- Agregaciones de citas y tamaño promedio por época.
- Uso automático de `mongomock` si no se puede conectar a MongoDB.

### 4. Visualización y dashboard

El dashboard **«¿Qué dataset de ciberseguridad me conviene?»** permite:

- Filtrar por año, tipo de datos, entorno, etiquetado y tamaño máximo.
- Consultar indicadores de cantidad, proporción de conjuntos con red y host, porcentaje etiquetado y tamaño mediano.
- Explorar gráficos de distribución temporal, citas, entornos, tamaños y procedencia del tráfico benigno.
- Revisar una tabla de datasets que cumplen los filtros, ordenada por citas.
- Descargar la selección filtrada en formato CSV.

## Estructura del proyecto

```text
proyecto/
├── proyecto_integrador_.ipynb  # Notebook principal
├── datasets.csv                # Catálogo de entrada (requerido)
├── limpieza.py                 # Generado desde el notebook
├── app.py                      # Dashboard generado desde el notebook
├── datasets_limpio.csv        # Salida generada después de la limpieza
└── README.md
```

> **Nota:** `limpieza.py`, `app.py` y `datasets_limpio.csv` se generan al ejecutar las respectivas celdas del notebook. El archivo `datasets.csv` es necesario y debe obtenerse por separado; no viene integrado en el notebook.

## Ejecución en Google Colab

1. Abre `proyecto_integrador_.ipynb` en Google Colab.
2. Ejecuta la primera celda para instalar Java 17 y las dependencias del entorno de Colab.
3. Sube el archivo `datasets.csv` cuando el notebook lo solicite. Debe conservar el nombre indicado y su estructura original.
4. Ejecuta las siguientes celdas **en orden**. Se crearán `limpieza.py` y `app.py`, se limpiarán los datos y se realizarán los análisis con Spark y MongoDB.
5. Para iniciar el dashboard, ejecuta la última celda. Esta pone en marcha Streamlit en el puerto `8501` y crea un túnel temporal con Cloudflare para acceder a la aplicación desde el navegador.

El notebook incluye validaciones `assert` sobre el número de registros y la coherencia de distintos resultados. Está preparado para un catálogo de **61 registros tras la limpieza**; si se usa otra versión del archivo CSV, es posible que deban adaptarse dichas validaciones.

## Ejecución local del dashboard

Si ya cuentas con `app.py`, `limpieza.py` y `datasets.csv` en la misma carpeta, puedes ejecutar el dashboard de forma independiente:

```bash
pip install pandas numpy plotly "streamlit>=1.50"
streamlit run app.py
```

Streamlit mostrará una dirección local (habitualmente `http://localhost:8501`). Para reproducir **todo el notebook**, también se requiere instalar y configurar las demás dependencias, incluida una instalación compatible de Java para PySpark.

## Datos de entrada

El archivo `datasets.csv` corresponde a un catálogo de datasets de ciberseguridad. Entre sus columnas utilizadas por el proyecto están `Name`, `Start Year`, `End Year`, `Network Data`, `Host Data`, `Setting`, `OS Type`, `Attack Categories`, `Packed Size in MB`, `Unpacked Size in MB` y `Times Recently Cited`.

Este proyecto **analiza metadatos de datasets**, no los registros originales de tráfico de red ni entrena modelos de detección de intrusiones.

## Resultados esperados

La ejecución produce un catálogo depurado, consultas y agregaciones sobre sus características, visualizaciones estadísticas y una herramienta interactiva para comparar opciones de datasets. Los valores obtenidos dependen del archivo CSV proporcionado.

## Autor

**Maria Paula Salamanca Gómez**  
Ingeniería de Sistemas — Proyecto académico
