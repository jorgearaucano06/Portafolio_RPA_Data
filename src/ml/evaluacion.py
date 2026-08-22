"""
Fase 6 — Evaluacion, tracking y serializacion de modelos.

Funciones para:
- Guardar resultados de entrenamiento en JSON (tracking local)
- Serializar/deserializar modelos con joblib
- Generar tabla comparativa de modelos

En Fase 8, el tracking local migra a MLflow en Databricks.

Uso:
    from src.ml.evaluacion import guardar_resultados, serializar_modelo, cargar_modelo
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib

from config.settings import settings

logger = logging.getLogger(__name__)


def guardar_resultados(
    resultados: list[dict],
    ruta: Path | str | None = None,
) -> Path:
    """Guarda resultados de entrenamiento en JSON.

    Parametros
    ----------
    resultados : list[dict]
        Lista de resultados (output de entrenar_regresores).
        Los objetos modelo se excluyen del JSON.
    ruta : Path, opcional
        Ruta al archivo JSON. Default: models/metricas/resultados_ml.json.

    Returns
    -------
    Path
        Ruta al archivo guardado.
    """
    ruta = Path(ruta or settings.ml.dir_metricas / "resultados_ml.json")
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # Cargar historial o crear nuevo
    historial = []
    if ruta.exists():
        with open(ruta, "r", encoding="utf-8") as f:
            historial = json.load(f)

    # Limpiar objetos no serializables
    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modelos": [],
    }
    for r in resultados:
        modelo_info = {
            "nombre": r["nombre"],
            "metricas_test": r.get("metricas_test", {}),
            "metricas_cv": r.get("metricas_cv", {}),
            "feature_importance": {
                k: float(v) for k, v in list(r.get("feature_importance", {}).items())[:10]
            },
        }
        entrada["modelos"].append(modelo_info)

    historial.append(entrada)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2, ensure_ascii=False)

    logger.info("Resultados guardados en %s", ruta)
    return ruta


def guardar_resultados_clustering(
    resultado: dict,
    ruta: Path | str | None = None,
) -> Path:
    """Guarda resultados de clustering en JSON.

    Parametros
    ----------
    resultado : dict
        Output de entrenar_clustering.
    ruta : Path, opcional
        Ruta al archivo JSON.

    Returns
    -------
    Path
    """
    ruta = Path(ruta or settings.ml.dir_metricas / "resultados_clustering.json")
    ruta.parent.mkdir(parents=True, exist_ok=True)

    historial = []
    if ruta.exists():
        with open(ruta, "r", encoding="utf-8") as f:
            historial = json.load(f)

    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "k_optimo": resultado["k_optimo"],
        "silhouette_kmeans": resultado["silhouette_kmeans"],
        "silhouette_dbscan": resultado["silhouette_dbscan"],
        "n_clusters_dbscan": resultado["n_clusters_dbscan"],
        "n_ruido_dbscan": resultado["n_ruido_dbscan"],
        "elbow_data": resultado["elbow_data"],
    }
    historial.append(entrada)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2, ensure_ascii=False)

    logger.info("Resultados de clustering guardados en %s", ruta)
    return ruta


def serializar_modelo(
    modelo: Any,
    nombre: str,
    directorio: Path | str | None = None,
) -> Path:
    """Serializa un modelo entrenado con joblib.

    Parametros
    ----------
    modelo : Any
        Modelo entrenado (sklearn, scaler, etc.).
    nombre : str
        Nombre del archivo (sin extension).
    directorio : Path, opcional
        Directorio de salida. Default: models/.

    Returns
    -------
    Path
        Ruta al archivo serializado.
    """
    directorio = Path(directorio or settings.ml.dir_modelos)
    directorio.mkdir(parents=True, exist_ok=True)

    ruta = directorio / f"{nombre}.joblib"
    joblib.dump(modelo, ruta)
    logger.info("Modelo serializado: %s", ruta)
    return ruta


def cargar_modelo(ruta: Path | str) -> Any:
    """Carga un modelo serializado con joblib.

    Parametros
    ----------
    ruta : Path o str
        Ruta al archivo .joblib.

    Returns
    -------
    Any
        Modelo deserializado.
    """
    ruta = Path(ruta)
    modelo = joblib.load(ruta)
    logger.info("Modelo cargado: %s", ruta)
    return modelo


def tabla_comparativa(resultados: list[dict]) -> str:
    """Genera una tabla formateada comparando modelos.

    Parametros
    ----------
    resultados : list[dict]
        Output de entrenar_regresores.

    Returns
    -------
    str
        Tabla formateada para logging/print.
    """
    lineas = [
        f"{'Modelo':<22s} {'RMSE':>12s} {'MAE':>12s} {'R2 Test':>10s} {'R2 CV':>10s}",
        "-" * 68,
    ]
    for r in resultados:
        mt = r["metricas_test"]
        mc = r["metricas_cv"]
        lineas.append(
            f"{r['nombre']:<22s} "
            f"{mt['rmse']:>12,.2f} "
            f"{mt['mae']:>12,.2f} "
            f"{mt['r2']:>10.4f} "
            f"{mc['r2_mean']:>10.4f}"
        )
    return "\n".join(lineas)
