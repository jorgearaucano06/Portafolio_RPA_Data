"""
Fase 9 — Dashboard avanzado v2.

Evoluciona el dashboard v1 (SQLite + barras basicas) a un dashboard
con 4 secciones: descriptiva, predictiva, clustering y benchmark.

Lee datos desde Parquet pre-procesado o CSV + filtros en tiempo real.
Carga modelos serializados de models/ para predicciones.

Ejecucion:
    streamlit run app_dashboard_v2.py
"""

import os
import sys
from pathlib import Path

# Agregar raiz del proyecto al path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import streamlit as st

from config.settings import settings

st.set_page_config(
    page_title="Pipeline MEF v2 — Dashboard",
    page_icon="📊",
    layout="wide",
)


def formatear_moneda(monto):
    """Formato financiero: S/. 1.5M, S/. 830.5K, etc."""
    if monto >= 1_000_000:
        return f"S/. {monto / 1_000_000:.1f}M"
    elif monto >= 1_000:
        return f"S/. {monto / 1_000:.1f}K"
    return f"S/. {monto:,.2f}"


@st.cache_data
def cargar_datos():
    """Carga datos desde Parquet procesado o CSV de sample."""
    dir_processed = settings.data.dir_processed
    ruta_sample = ROOT / "tests" / "data" / "sample_gasto.csv"

    # Intentar Parquet primero, luego CSV raw, luego sample
    if dir_processed.exists() and any(dir_processed.glob("**/*.parquet")):
        df = pd.read_parquet(dir_processed)
        fuente = "Parquet procesado"
    elif settings.data.ruta_csv_raw.exists():
        df = pd.read_csv(settings.data.ruta_csv_raw, encoding="utf-8")
        # Aplicar filtros basicos
        df = df[df["MONTO_DEVENGADO"] > 0].dropna(subset=["DISTRITO_EJECUTORA_NOMBRE"])
        df = df[df["DISTRITO_EJECUTORA_NOMBRE"].str.strip() != ""]
        fuente = "CSV crudo (con filtros)"
    elif ruta_sample.exists():
        df = pd.read_csv(ruta_sample)
        df = df[pd.to_numeric(df["MONTO_DEVENGADO"], errors="coerce") > 0]
        df["MONTO_DEVENGADO"] = pd.to_numeric(df["MONTO_DEVENGADO"], errors="coerce")
        df = df.dropna(subset=["DISTRITO_EJECUTORA_NOMBRE", "MONTO_DEVENGADO"])
        df = df[df["DISTRITO_EJECUTORA_NOMBRE"].str.strip() != ""]
        fuente = "Sample de tests (50 filas)"
    else:
        return pd.DataFrame(), "Sin datos"

    return df, fuente


@st.cache_resource
def cargar_modelo_regresion():
    """Intenta cargar el mejor modelo de regresion serializado."""
    dir_modelos = settings.ml.dir_modelos
    if not dir_modelos.exists():
        return None

    import glob
    modelos = glob.glob(str(dir_modelos / "mejor_regresor_*.joblib"))
    if not modelos:
        return None

    import joblib
    return joblib.load(modelos[0])


def seccion_descriptiva(df, col_depto, col_sector):
    """Seccion 1: KPIs y distribucion del gasto."""
    st.header("Analisis Descriptivo")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registros", f"{len(df):,}")
    with col2:
        st.metric("Gasto Total", formatear_moneda(df["MONTO_DEVENGADO"].sum()))
    with col3:
        st.metric("Gasto Promedio", formatear_moneda(df["MONTO_DEVENGADO"].mean()))
    with col4:
        n_deptos = df[col_depto].nunique() if col_depto in df.columns else 0
        st.metric("Jurisdicciones", n_deptos)

    st.markdown("---")

    # Graficos lado a lado
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("Gasto por departamento/distrito")
        if col_depto in df.columns:
            por_depto = (
                df.groupby(col_depto)["MONTO_DEVENGADO"]
                .sum()
                .sort_values(ascending=False)
                .head(15)
                .reset_index()
            )
            por_depto.columns = ["Jurisdiccion", "Gasto Total"]
            st.bar_chart(por_depto, x="Jurisdiccion", y="Gasto Total")

    with col_der:
        st.subheader("Gasto por sector")
        if col_sector in df.columns:
            por_sector = (
                df.groupby(col_sector)["MONTO_DEVENGADO"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            por_sector.columns = ["Sector", "Gasto Total"]
            st.bar_chart(por_sector, x="Sector", y="Gasto Total")


def seccion_predictiva(df):
    """Seccion 2: Predicciones del modelo (si esta disponible)."""
    st.header("Analisis Predictivo")

    modelo = cargar_modelo_regresion()
    if modelo is None:
        st.info(
            "No hay modelos entrenados todavia. "
            "Ejecuta el notebook 02_ml_sklearn.ipynb para entrenar modelos "
            "y luego recarga este dashboard."
        )
        return

    st.success("Modelo de regresion cargado.")

    # Mostrar metricas del modelo si hay archivo de resultados
    ruta_metricas = settings.ml.dir_metricas / "resultados_ml.json"
    if ruta_metricas.exists():
        import json
        with open(ruta_metricas, "r") as f:
            historial = json.load(f)

        if historial:
            ultimo = historial[-1]
            st.subheader("Metricas del ultimo entrenamiento")
            cols = st.columns(len(ultimo["modelos"]))
            for i, m in enumerate(ultimo["modelos"]):
                with cols[i]:
                    st.markdown(f"**{m['nombre']}**")
                    mt = m["metricas_test"]
                    st.metric("R2", f"{mt['r2']:.4f}")
                    st.metric("RMSE", f"{mt['rmse']:,.2f}")
                    st.metric("MAE", f"{mt['mae']:,.2f}")


def seccion_clustering(df, col_depto, col_sector):
    """Seccion 3: Resultados de clustering."""
    st.header("Clustering de Jurisdicciones")

    ruta_clustering = settings.ml.dir_metricas / "resultados_clustering.json"
    if not ruta_clustering.exists():
        st.info(
            "No hay resultados de clustering. "
            "Ejecuta el notebook 02_ml_sklearn.ipynb primero."
        )
        return

    import json
    with open(ruta_clustering, "r") as f:
        historial = json.load(f)

    if not historial:
        return

    ultimo = historial[-1]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("K optimo (KMeans)", ultimo["k_optimo"])
    with col2:
        st.metric("Silhouette KMeans", f"{ultimo['silhouette_kmeans']:.4f}")
    with col3:
        st.metric("Clusters DBSCAN", ultimo["n_clusters_dbscan"])

    # Elbow chart
    if "elbow_data" in ultimo:
        elbow = ultimo["elbow_data"]
        elbow_df = pd.DataFrame({
            "K": elbow["k_values"],
            "Silhouette": elbow["silhouettes"],
        })
        st.subheader("Silhouette Score por K")
        st.line_chart(elbow_df, x="K", y="Silhouette")


def seccion_benchmark():
    """Seccion 4: Comparativa v1 vs v2."""
    st.header("Benchmark v1 vs v2")

    st.markdown("""
    | Aspecto | v1 (SQLite) | v2 (Spark + ML) |
    |---------|------------|-----------------|
    | Motor de datos | SQLite (single-core) | PySpark (multi-core) |
    | Formato de almacenamiento | SQLite .db | Parquet particionado |
    | Procesamiento | Python fila a fila | Spark paralelo por particiones |
    | Volumen maximo | ~40 MB (muestra) | Dataset completo (500 MB+) |
    | Filtros de calidad | CSV + Python | Spark filter/withColumn |
    | Logging | print() | stdlib logging profesional |
    | Tests | Ninguno | pytest (20+ tests) |
    | ML | Ninguno | scikit-learn + MLlib |
    | Dashboard | KPIs basicos | Descriptivo + Predictivo + Clustering |
    """)

    st.info(
        "Las metricas de rendimiento reales (tiempos, registros/segundo) "
        "se completaran al ejecutar el pipeline completo con el dataset real."
    )


def main():
    st.title("Pipeline MEF v2 — Dashboard Ejecutivo")
    st.markdown("Analisis integral del gasto publico: descriptivo, predictivo y clustering.")

    resultado = cargar_datos()
    if isinstance(resultado, tuple):
        df, fuente = resultado
    else:
        df, fuente = pd.DataFrame(), "Error"

    if df.empty:
        st.error("No se encontraron datos. Ejecuta el pipeline de ingesta primero.")
        return

    st.caption(f"Fuente de datos: {fuente} | {len(df):,} registros")

    # Detectar nombre de columna de departamento
    col_depto = "DEPARTAMENTO_EJECUTORA_NOMBRE" if "DEPARTAMENTO_EJECUTORA_NOMBRE" in df.columns else "DISTRITO_EJECUTORA_NOMBRE"
    col_sector = "SECTOR_NOMBRE"

    # Sidebar — filtros
    st.sidebar.title("Filtros")

    if col_depto in df.columns:
        deptos = sorted(df[col_depto].dropna().unique().tolist())
        seleccion_deptos = st.sidebar.multiselect(
            "Departamentos/Distritos:",
            options=deptos,
            default=deptos[:5],
        )
        if seleccion_deptos:
            df = df[df[col_depto].isin(seleccion_deptos)]

    if col_sector in df.columns:
        sectores = sorted(df[col_sector].dropna().unique().tolist())
        seleccion_sectores = st.sidebar.multiselect(
            "Sectores:",
            options=sectores,
            default=sectores,
        )
        if seleccion_sectores:
            df = df[df[col_sector].isin(seleccion_sectores)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Registros filtrados: {len(df):,}")

    # Tabs para las secciones
    tab1, tab2, tab3, tab4 = st.tabs([
        "Descriptivo", "Predictivo", "Clustering", "Benchmark v1 vs v2",
    ])

    with tab1:
        seccion_descriptiva(df, col_depto, col_sector)
    with tab2:
        seccion_predictiva(df)
    with tab3:
        seccion_clustering(df, col_depto, col_sector)
    with tab4:
        seccion_benchmark()


if __name__ == "__main__":
    main()
