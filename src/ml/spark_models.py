"""
Fase 7 — Pipeline de ML distribuido con PySpark MLlib.

Replica los modelos de scikit-learn (Fase 6) usando MLlib para demostrar
procesamiento de ML a escala. El pipeline de MLlib encadena:

    StringIndexer -> OneHotEncoder -> VectorAssembler -> Modelo -> Evaluacion

Uso:
    from src.ml.spark_models import crear_pipeline_regresion, evaluar_modelo_spark
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.ml import PipelineModel
    from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)


def crear_pipeline_regresion(
    df: DataFrame,
    target: str = "MONTO_DEVENGADO",
    categoricas: list[str] | None = None,
    modelo_tipo: str = "random_forest",
    test_size: float = 0.2,
    seed: int = 42,
) -> dict:
    """Crea y entrena un pipeline de regresion MLlib.

    Parametros
    ----------
    df : DataFrame
        DataFrame de Spark con datos limpios.
    target : str
        Columna objetivo.
    categoricas : list[str], opcional
        Columnas categoricas. Por defecto: SECTOR_NOMBRE, NIVEL_GOBIERNO_NOMBRE, MES_EJE.
    modelo_tipo : str
        Tipo de modelo: "linear", "random_forest", "gbt".
    test_size : float
        Proporcion del test set.
    seed : int
        Semilla para reproducibilidad.

    Returns
    -------
    dict
        Contiene: pipeline_model, metricas, df_predicciones.
    """
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import (
        OneHotEncoder,
        StringIndexer,
        VectorAssembler,
    )
    from pyspark.ml.regression import (
        GBTRegressor,
        LinearRegression,
        RandomForestRegressor,
    )

    if categoricas is None:
        candidatas = ["SECTOR_NOMBRE", "NIVEL_GOBIERNO_NOMBRE", "MES_EJE"]
        categoricas = [c for c in candidatas if c in df.columns]

    logger.info("Pipeline MLlib — modelo: %s, categoricas: %s", modelo_tipo, categoricas)

    # Etapas del pipeline
    stages = []

    # StringIndexer + OneHotEncoder para cada categorica
    encoded_cols = []

    for col_name in categoricas:
        idx_col = f"{col_name}_idx"
        enc_col = f"{col_name}_enc"

        indexer = StringIndexer(
            inputCol=col_name, outputCol=idx_col, handleInvalid="keep",
        )
        encoder = OneHotEncoder(inputCol=idx_col, outputCol=enc_col)

        stages.extend([indexer, encoder])
        encoded_cols.append(enc_col)

    # VectorAssembler: combina todas las features en un vector
    assembler = VectorAssembler(
        inputCols=encoded_cols, outputCol="features", handleInvalid="skip",
    )
    stages.append(assembler)

    # Modelo
    modelos = {
        "linear": LinearRegression(
            featuresCol="features", labelCol=target, maxIter=100,
        ),
        "random_forest": RandomForestRegressor(
            featuresCol="features", labelCol=target,
            numTrees=100, seed=seed,
        ),
        "gbt": GBTRegressor(
            featuresCol="features", labelCol=target,
            maxIter=100, seed=seed,
        ),
    }

    if modelo_tipo not in modelos:
        raise ValueError(f"Modelo no soportado: {modelo_tipo}. Opciones: {list(modelos.keys())}")

    stages.append(modelos[modelo_tipo])

    # Split y entrenamiento
    train_df, test_df = df.randomSplit([1 - test_size, test_size], seed=seed)
    logger.info("Split: train=%d, test=%d", train_df.count(), test_df.count())

    pipeline = Pipeline(stages=stages)
    pipeline_model = pipeline.fit(train_df)

    # Predicciones
    predictions = pipeline_model.transform(test_df)

    # Evaluacion
    metricas = evaluar_modelo_spark(predictions, target)

    logger.info(
        "%s -> RMSE=%.2f, MAE=%.2f, R2=%.4f",
        modelo_tipo, metricas["rmse"], metricas["mae"], metricas["r2"],
    )

    return {
        "pipeline_model": pipeline_model,
        "metricas": metricas,
        "df_predicciones": predictions,
        "modelo_tipo": modelo_tipo,
    }


def evaluar_modelo_spark(
    predictions: DataFrame,
    target: str = "MONTO_DEVENGADO",
) -> dict:
    """Evalua predicciones de un modelo MLlib.

    Parametros
    ----------
    predictions : DataFrame
        DataFrame con columnas 'prediction' y target.
    target : str
        Columna real.

    Returns
    -------
    dict
        Metricas: rmse, mae, r2.
    """
    from pyspark.ml.evaluation import RegressionEvaluator

    evaluadores = {
        "rmse": RegressionEvaluator(
            labelCol=target, predictionCol="prediction", metricName="rmse",
        ),
        "mae": RegressionEvaluator(
            labelCol=target, predictionCol="prediction", metricName="mae",
        ),
        "r2": RegressionEvaluator(
            labelCol=target, predictionCol="prediction", metricName="r2",
        ),
    }

    return {nombre: float(ev.evaluate(predictions)) for nombre, ev in evaluadores.items()}


def comparar_sklearn_vs_mllib(
    resultados_sklearn: list[dict],
    resultados_mllib: list[dict],
) -> str:
    """Genera tabla comparativa sklearn vs MLlib.

    Parametros
    ----------
    resultados_sklearn : list[dict]
        Output de entrenar_regresores.
    resultados_mllib : list[dict]
        Lista de outputs de crear_pipeline_regresion.

    Returns
    -------
    str
        Tabla formateada.
    """
    lineas = [
        f"{'Framework':<12s} {'Modelo':<18s} {'RMSE':>12s} {'MAE':>12s} {'R2':>10s}",
        "-" * 66,
    ]

    for r in resultados_sklearn:
        mt = r["metricas_test"]
        lineas.append(
            f"{'sklearn':<12s} {r['nombre']:<18s} "
            f"{mt['rmse']:>12,.2f} {mt['mae']:>12,.2f} {mt['r2']:>10.4f}"
        )

    for r in resultados_mllib:
        mt = r["metricas"]
        lineas.append(
            f"{'MLlib':<12s} {r['modelo_tipo']:<18s} "
            f"{mt['rmse']:>12,.2f} {mt['mae']:>12,.2f} {mt['r2']:>10.4f}"
        )

    return "\n".join(lineas)
