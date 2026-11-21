"""Limpieza compartida por el notebook y el dashboard (una sola fuente de verdad)."""
import numpy as np
import pandas as pd

ANIO_ACTUAL = 2026
CENTINELAS = ["-", "PARSE_ERROR", ""]  # formas en que el catálogo codifica "dato faltante"
COLS_BOOL = ["red", "host", "etiquetado", "tiene_windows", "tiene_linux"]


def leer_crudo(ruta="datasets.csv"):
    # keep_default_na=False: pandas convertiría "None" y "n/a" en NaN, y aquí son valores con significado.
    return pd.read_csv(ruta, sep=";", dtype=str, keep_default_na=False)


def _etiqueta(texto, existe):
    if existe == "No":
        return "No aplica"  # no hay datos de ese tipo, no tiene sentido etiquetarlos
    t = texto.lower()
    if t.startswith("no"):
        return "No"
    if t.startswith("yes") or "ground truth" in t or "flows are labeled" in t:
        return "Sí"
    return "Sin dato"  # "-", PARSE_ERROR, "Presumably"


def _benigno(texto):
    t = texto.lower()
    if "synthetic" in t and "real humans" in t:
        return "Mixto"
    if t.startswith("real"):
        return "Real"
    if "synthetic" in t:
        return "Sintético"
    if t == "none":
        return "Ninguno"
    if t == "n/a":
        return "No aplica"
    if t.startswith("present"):
        return "No especificado"
    return "Sin dato"


def limpiar(raw):
    df = raw.copy()
    df.columns = [c.strip() for c in df.columns]
    df = df.apply(lambda s: s.str.strip()).drop_duplicates()
    o = pd.DataFrame({"nombre": df["Name"]})
    o["anio_inicio"] = df["Start Year"].astype(int)
    o["anio_fin"] = df["End Year"].astype(int)
    o["epoca"] = pd.cut(o.anio_fin, [1990, 2009, 2015, 2020, 2026],
                        labels=["1998-2009", "2010-2015", "2016-2020", "2021-2025"]).astype(str)
    o["red"] = df["Network Data"].eq("Yes")
    o["host"] = df["Host Data"].eq("Yes")
    o["tipo_datos"] = np.select([o.red & o.host, o.red, o.host], ["Red + Host", "Solo red", "Solo host"], "Ninguno")
    o["entorno"] = df["Setting"].replace({"Undisclosed": "No declarado"})
    o["so"] = df["OS Type"].replace({"Undisclosed": "No declarado"})
    o["tiene_windows"] = df["OS Type"].str.contains("Windows")
    o["tiene_linux"] = df["OS Type"].str.contains("Linux")
    o["etiq_red"] = [_etiqueta(t, e) for t, e in zip(df["Network Data Labeled"], df["Network Data"])]
    o["etiq_host"] = [_etiqueta(t, e) for t, e in zip(df["Host Data Labeled"], df["Host Data"])]
    o["etiquetado"] = (o.etiq_red == "Sí") | (o.etiq_host == "Sí")
    o["ataques"] = df["Attack Categories"].replace({"": "No especificado", "-": "No especificado", "n/a": "No aplica"})
    o["trafico_benigno"] = df["Benign Activity"].map(_benigno)
    for src, dst in [("Packed Size in MB", "empaquetado_mb"), ("Unpacked Size in MB", "descomprimido_mb"),
                     ("Times Recently Cited", "citas")]:
        o[dst] = pd.to_numeric(df[src].replace(CENTINELAS, np.nan), errors="coerce")
    o[["empaquetado_mb", "descomprimido_mb"]] = o[["empaquetado_mb", "descomprimido_mb"]].round(1)
    o["tamano_gb"] = (o.descomprimido_mb.fillna(o.empaquetado_mb) / 1024).round(2)
    o["categoria_tamano"] = pd.cut(o.tamano_gb, [0, 1, 10, 100, 1024, np.inf],
                                   labels=["<1 GB", "1-10 GB", "10-100 GB", "100 GB-1 TB", ">1 TB"]).astype(object).fillna("Sin dato")
    o["antiguedad"] = ANIO_ACTUAL - o.anio_fin
    return o.reset_index(drop=True)


def para_csv(df):
    """Booleanos como 0/1 para que Spark los infiera como enteros sin ambigüedad."""
    return df.astype({c: int for c in COLS_BOOL})
