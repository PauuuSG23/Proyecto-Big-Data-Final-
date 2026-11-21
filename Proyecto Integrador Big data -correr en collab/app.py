from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from limpieza import leer_crudo, limpiar

st.set_page_config(page_title="Datasets de ciberseguridad", layout="wide")
SIN_LIMITE = 10_000_000


@st.cache_data
def cargar():
    return limpiar(leer_crudo(Path(__file__).parent / "datasets.csv"))


df = cargar()

st.title("¿Qué dataset de ciberseguridad me conviene?")
st.caption("Catálogo de 61 datasets para detección de intrusiones. Filtra según tu caso de uso.")

# ---- Filtros (barra lateral)
st.sidebar.header("Filtros")
a_min, a_max = int(df.anio_fin.min()), int(df.anio_fin.max())
anios = st.sidebar.slider("Año de publicación", a_min, a_max, (2015, a_max))
tipos = st.sidebar.multiselect("Tipo de datos", sorted(df.tipo_datos.unique()), default=sorted(df.tipo_datos.unique()))
entornos = st.sidebar.multiselect("Entorno", sorted(df.entorno.unique()), default=sorted(df.entorno.unique()))
solo_etiq = st.sidebar.checkbox("Solo datasets etiquetados")
max_gb = st.sidebar.select_slider(
    "Tamaño máximo", [1, 10, 50, 100, 1024, SIN_LIMITE], value=SIN_LIMITE,
    format_func=lambda v: "Sin límite" if v == SIN_LIMITE else (f"{v} GB" if v < 1024 else "1 TB"))

f = df[df.anio_fin.between(*anios) & df.tipo_datos.isin(tipos) & df.entorno.isin(entornos)]
if solo_etiq:
    f = f[f.etiquetado]
f = f[(f.tamano_gb <= max_gb) | (f.tamano_gb.isna() & (max_gb == SIN_LIMITE))]

if f.empty:
    st.warning("Ningún dataset cumple los filtros. Relaja alguno.")
    st.stop()

# ---- KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Datasets", len(f))
k2.metric("Con red + host", f"{(f.tipo_datos == 'Red + Host').mean():.0%}")
k3.metric("Etiquetados", f"{f.etiquetado.mean():.0%}")
k4.metric("Tamaño mediano", "s/d" if f.tamano_gb.isna().all() else f"{f.tamano_gb.median():.1f} GB")

# ---- Gráficos (Plotly)
c1, c2 = st.columns(2)
c1.plotly_chart(px.histogram(f, x="anio_fin", color="tipo_datos", title="Datasets por año y tipo de datos",
                             labels={"anio_fin": "Año", "count": "Datasets"}), use_container_width=True)
cit = f[f.citas > 0]
c2.plotly_chart(px.scatter(cit, x="anio_fin", y="citas", color="tipo_datos", hover_name="nombre", log_y=True,
                           title="Citas recientes vs. año (escala log)", labels={"anio_fin": "Año"}),
                use_container_width=True)
c3, c4 = st.columns(2)
c3.plotly_chart(px.bar(f.groupby(["entorno", "tipo_datos"]).size().reset_index(name="n"), x="entorno", y="n",
                       color="tipo_datos", title="Entornos cubiertos"), use_container_width=True)
c4.plotly_chart(px.box(f.dropna(subset=["tamano_gb"]), x="tipo_datos", y="tamano_gb", points="all",
                       hover_name="nombre", log_y=True, title="Tamaño en disco (GB, escala log)"),
                use_container_width=True)
c5, _ = st.columns(2)
c5.plotly_chart(px.pie(f, names="trafico_benigno", hole=0.45, title="Origen del tráfico benigno"),
                use_container_width=True)

# ---- Tabla y descarga
st.subheader("Datasets que cumplen tus filtros")
tabla = f[["nombre", "anio_fin", "tipo_datos", "entorno", "so", "etiquetado", "tamano_gb", "citas", "ataques"]]
tabla = tabla.sort_values("citas", ascending=False, na_position="last")
st.dataframe(tabla, use_container_width=True, hide_index=True)
st.download_button("Descargar selección (CSV)", tabla.to_csv(index=False).encode("utf-8"), "seleccion.csv")
