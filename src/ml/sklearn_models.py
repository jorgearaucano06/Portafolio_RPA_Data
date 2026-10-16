"""
Fase 6 — Modelos de ML con scikit-learn.

Dos familias de modelos:
1. Regresion: predecir MONTO_DEVENGADO a partir de departamento, sector, mes, etc.
2. Clustering: agrupar jurisdicciones por patrones de gasto similares.

Cada funcion devuelve el modelo entrenado + metricas, sin efectos secundarios.
La serializacion y el tracking se manejan en evaluacion.py.

Uso:
    from src.ml.sklearn_models import entrenar_regresores, entrenar_clustering
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from config.settings import settings

logger = logging.getLogger(__name__)


def entrenar_regresores(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    test_size: float | None = None,
    random_state: int | None = None,
    cv_folds: int = 5,
) -> list[dict]:
    """Entrena y evalua 3 regresores sobre los datos.

    Modelos: Linear Regression, Random Forest, Gradient Boosting.
    Evaluacion: train/test split + cross-validation.

    Parametros
    ----------
    X : pd.DataFrame
        Features (ya encodeadas).
    y : pd.Series
        Target (MONTO_DEVENGADO).
    test_size : float, opcional
        Proporcion del test set. Default: settings.ml.test_size.
    random_state : int, opcional
        Semilla. Default: settings.ml.random_state.
    cv_folds : int
        Folds para cross-validation.

    Returns
    -------
    list[dict]
        Lista de resultados, uno por modelo. Cada dict contiene:
        nombre, modelo, metricas_test, metricas_cv, feature_importance.
    """
    test_size = test_size or settings.ml.test_size
    random_state = random_state or settings.ml.random_state

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state,
    )
    logger.info("Split: train=%d, test=%d", len(X_train), len(X_test))

    modelos = [
        ("LinearRegression", LinearRegression()),
        ("RandomForest", RandomForestRegressor(
            n_estimators=100, random_state=random_state, n_jobs=-1,
        )),
        ("GradientBoosting", GradientBoostingRegressor(
            n_estimators=100, random_state=random_state,
        )),
    ]

    resultados = []

    for nombre, modelo in modelos:
        logger.info("Entrenando %s...", nombre)
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)

        # Metricas en test set
        metricas_test = {
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
        }

        # Cross-validation (R2 por defecto)
        cv_scores = cross_val_score(
            modelo, X, y, cv=cv_folds, scoring="r2", n_jobs=-1,
        )
        metricas_cv = {
            "r2_mean": float(cv_scores.mean()),
            "r2_std": float(cv_scores.std()),
            "r2_scores": [float(s) for s in cv_scores],
        }

        # Feature importance (si el modelo la tiene)
        importance = {}
        if hasattr(modelo, "feature_importances_"):
            imp = modelo.feature_importances_
            importance = dict(sorted(
                zip(X.columns, imp), key=lambda x: x[1], reverse=True,
            ))
        elif hasattr(modelo, "coef_"):
            coef = np.abs(modelo.coef_)
            importance = dict(sorted(
                zip(X.columns, coef), key=lambda x: x[1], reverse=True,
            ))

        logger.info(
            "%s -> RMSE=%.2f, MAE=%.2f, R2=%.4f (CV R2=%.4f +/- %.4f)",
            nombre, metricas_test["rmse"], metricas_test["mae"],
            metricas_test["r2"], metricas_cv["r2_mean"], metricas_cv["r2_std"],
        )

        resultados.append({
            "nombre": nombre,
            "modelo": modelo,
            "metricas_test": metricas_test,
            "metricas_cv": metricas_cv,
            "feature_importance": importance,
        })

    return resultados


def entrenar_clustering(
    df_features: pd.DataFrame,
    df_info: pd.DataFrame,
    *,
    max_k: int = 10,
    random_state: int | None = None,
) -> dict:
    """Entrena KMeans y DBSCAN sobre features agregadas.

    Incluye Elbow Method para determinar el K optimo.

    Parametros
    ----------
    df_features : pd.DataFrame
        Features numericas (output de preparar_features_clustering).
    df_info : pd.DataFrame
        Etiquetas de cada grupo (departamento, sector).
    max_k : int
        K maximo para Elbow Method.
    random_state : int, opcional
        Semilla.

    Returns
    -------
    dict
        Contiene: kmeans_modelo, dbscan_modelo, k_optimo, labels_kmeans,
        labels_dbscan, silhouette_kmeans, silhouette_dbscan, elbow_data.
    """
    random_state = random_state or settings.ml.random_state

    # Normalizar features (KMeans es sensible a escala)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_features)

    # --- Elbow Method para encontrar K optimo ---
    max_k = min(max_k, len(df_features) - 1)
    inertias = []
    silhouettes = []
    k_range = range(2, max_k + 1)

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(float(km.inertia_))
        silhouettes.append(float(silhouette_score(X_scaled, labels)))

    # K optimo = el que maximiza silhouette
    k_optimo = list(k_range)[np.argmax(silhouettes)]
    logger.info("K optimo (max silhouette): %d", k_optimo)

    # --- KMeans con K optimo ---
    kmeans = KMeans(n_clusters=k_optimo, random_state=random_state, n_init=10)
    labels_km = kmeans.fit_predict(X_scaled)
    sil_km = float(silhouette_score(X_scaled, labels_km))
    logger.info("KMeans (k=%d): silhouette=%.4f", k_optimo, sil_km)

    # --- DBSCAN ---
    dbscan = DBSCAN(eps=1.5, min_samples=2)
    labels_db = dbscan.fit_predict(X_scaled)
    n_clusters_db = len(set(labels_db)) - (1 if -1 in labels_db else 0)
    n_ruido = int((labels_db == -1).sum())

    sil_db = None
    if n_clusters_db >= 2:
        mask = labels_db != -1
        if mask.sum() > n_clusters_db:
            sil_db = float(silhouette_score(X_scaled[mask], labels_db[mask]))
    logger.info("DBSCAN: %d clusters, %d ruido, silhouette=%s",
                n_clusters_db, n_ruido, f"{sil_db:.4f}" if sil_db else "N/A")

    return {
        "kmeans_modelo": kmeans,
        "dbscan_modelo": dbscan,
        "scaler": scaler,
        "k_optimo": k_optimo,
        "labels_kmeans": labels_km,
        "labels_dbscan": labels_db,
        "silhouette_kmeans": sil_km,
        "silhouette_dbscan": sil_db,
        "n_clusters_dbscan": n_clusters_db,
        "n_ruido_dbscan": n_ruido,
        "elbow_data": {
            "k_values": list(k_range),
            "inertias": inertias,
            "silhouettes": silhouettes,
        },
    }
