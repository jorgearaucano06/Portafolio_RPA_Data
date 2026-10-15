"""
Fase 6 — Feature engineering para modelos de ML.

Transforma los datos limpios del pipeline en features numericas listas
para entrenar modelos. Compartido entre scikit-learn (Fase 6) y MLlib (Fase 7).

Dos niveles de features:
1. Por registro individual (encoding de categoricas)
2. Por grupo (departamento x sector) con metricas agregadas — para clustering

Uso:
    from src.ml.features import preparar_features_registro, preparar_features_clustering
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def preparar_features_registro(
    df: pd.DataFrame,
    target: str = "MONTO_DEVENGADO",
    categoricas: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Prepara features a nivel de registro individual para regresion.

    Convierte columnas categoricas a dummies (one-hot encoding) y separa
    el target del resto de features.

    Parametros
    ----------
    df : pd.DataFrame
        DataFrame limpio (post-filtros UAT), ya en pandas.
    target : str
        Nombre de la columna objetivo.
    categoricas : list[str], opcional
        Columnas categoricas a encodear. Por defecto usa las mas relevantes.

    Returns
    -------
    tuple[pd.DataFrame, pd.Series, list[str]]
        (X, y, nombres_features)
    """
    if categoricas is None:
        # Seleccionamos las categoricas que aportan informacion
        candidatas = [
            "SECTOR_NOMBRE",
            "NIVEL_GOBIERNO_NOMBRE",
            "DEPARTAMENTO_EJECUTORA_NOMBRE",
            "MES_EJE",
        ]
        categoricas = [c for c in candidatas if c in df.columns]

    logger.info("Features categoricas: %s", categoricas)
    logger.info("Target: %s", target)

    # One-hot encoding
    df_encoded = pd.get_dummies(df[categoricas], drop_first=True, dtype=int)

    X = df_encoded
    y = df[target]

    logger.info("Shape de X: %s, shape de y: %s", X.shape, y.shape)
    logger.info("Features generadas: %d", X.shape[1])

    return X, y, list(X.columns)


def preparar_features_clustering(
    df: pd.DataFrame,
    grupo: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prepara features agregadas por grupo para clustering.

    Agrupa por (departamento, sector) y calcula metricas de gasto.
    Cada fila del resultado representa un grupo, no un registro individual.

    Parametros
    ----------
    df : pd.DataFrame
        DataFrame limpio en pandas.
    grupo : list[str], opcional
        Columnas de agrupacion. Por defecto: departamento + sector.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (df_features, df_info) donde df_info contiene las etiquetas del grupo
        y df_features las columnas numericas normalizadas.
    """
    if grupo is None:
        candidatas = ["DEPARTAMENTO_EJECUTORA_NOMBRE", "SECTOR_NOMBRE"]
        grupo = [c for c in candidatas if c in df.columns]

    # Si no hay columnas de grupo, usamos lo que haya como categorica
    if not grupo:
        grupo = [df.select_dtypes(include="object").columns[0]]

    logger.info("Agrupando por: %s", grupo)

    agg = (
        df.groupby(grupo)["MONTO_DEVENGADO"]
        .agg(["sum", "mean", "median", "std", "count", "min", "max"])
        .reset_index()
    )
    agg.columns = grupo + [
        "total_monto", "promedio_monto", "mediana_monto",
        "std_monto", "num_registros", "monto_min", "monto_max",
    ]

    # Rellenar std NaN (grupos con 1 solo registro)
    agg["std_monto"] = agg["std_monto"].fillna(0)

    # Coeficiente de variacion: dispersion relativa
    agg["cv_monto"] = np.where(
        agg["promedio_monto"] > 0,
        agg["std_monto"] / agg["promedio_monto"],
        0,
    )

    # Rango como feature
    agg["rango_monto"] = agg["monto_max"] - agg["monto_min"]

    # Separar info (etiquetas) de features numericas
    cols_features = [
        "total_monto", "promedio_monto", "mediana_monto", "std_monto",
        "num_registros", "monto_min", "monto_max", "cv_monto", "rango_monto",
    ]

    df_info = agg[grupo].copy()
    df_features = agg[cols_features].copy()

    logger.info("Grupos generados: %d, features por grupo: %d",
                len(df_features), len(cols_features))

    return df_features, df_info
