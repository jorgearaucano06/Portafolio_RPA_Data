"""
Fase 2 — Lectura del CSV del MEF con schema explicito en Spark.

Usa StructType en lugar de inferSchema=True para:
- Evitar un scan completo del archivo (rendimiento)
- Garantizar tipos correctos desde el inicio
- Detectar cambios de formato en la fuente

Uso:
    from src.ingesta.lector_csv import leer_csv_con_schema

    df = leer_csv_con_schema(spark, ruta_csv)
"""

from __future__ import annotations

import logging
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

logger = logging.getLogger(__name__)

# Schema explicito del CSV de gasto publico del MEF.
# Columnas basadas en el formato real de:
# https://fs.datosabiertos.mef.gob.pe/datastorefiles/2020-Gasto.csv
#
# Todas las columnas se leen como String excepto MONTO_DEVENGADO (Double)
# porque es el campo numerico principal del pipeline.
# Las columnas extra del CSV que no estan en este schema se ignoran.
SCHEMA_GASTO_MEF = StructType([
    StructField("ANO_EJE", StringType(), True),
    StructField("MES_EJE", StringType(), True),
    StructField("NIVEL_GOBIERNO", StringType(), True),
    StructField("NIVEL_GOBIERNO_NOMBRE", StringType(), True),
    StructField("SECTOR", StringType(), True),
    StructField("SECTOR_NOMBRE", StringType(), True),
    StructField("PLIEGO", StringType(), True),
    StructField("PLIEGO_NOMBRE", StringType(), True),
    StructField("EJECUTORA", StringType(), True),
    StructField("EJECUTORA_NOMBRE", StringType(), True),
    StructField("DEPARTAMENTO_EJECUTORA", StringType(), True),
    StructField("DEPARTAMENTO_EJECUTORA_NOMBRE", StringType(), True),
    StructField("PROVINCIA_EJECUTORA", StringType(), True),
    StructField("PROVINCIA_EJECUTORA_NOMBRE", StringType(), True),
    StructField("DISTRITO_EJECUTORA", StringType(), True),
    StructField("DISTRITO_EJECUTORA_NOMBRE", StringType(), True),
    StructField("FUNCION", StringType(), True),
    StructField("FUNCION_NOMBRE", StringType(), True),
    StructField("DIVIDENDO_FUNCIONAL", StringType(), True),
    StructField("DIVIDENDO_FUNCIONAL_NOMBRE", StringType(), True),
    StructField("GRUPO_FUNCIONAL", StringType(), True),
    StructField("GRUPO_FUNCIONAL_NOMBRE", StringType(), True),
    StructField("ACTIVIDAD_PROYECTO", StringType(), True),
    StructField("ACTIVIDAD_PROYECTO_NOMBRE", StringType(), True),
    StructField("FUENTE_FINANCIAMIENTO", StringType(), True),
    StructField("FUENTE_FINANCIAMIENTO_NOMBRE", StringType(), True),
    StructField("RUBRO", StringType(), True),
    StructField("RUBRO_NOMBRE", StringType(), True),
    StructField("TIPO_RECURSO", StringType(), True),
    StructField("TIPO_RECURSO_NOMBRE", StringType(), True),
    StructField("CATEGORIA_GASTO", StringType(), True),
    StructField("CATEGORIA_GASTO_NOMBRE", StringType(), True),
    StructField("GENERICA", StringType(), True),
    StructField("GENERICA_NOMBRE", StringType(), True),
    StructField("SUBGENERICA", StringType(), True),
    StructField("SUBGENERICA_NOMBRE", StringType(), True),
    StructField("SUBGENERICA_DETALLE", StringType(), True),
    StructField("SUBGENERICA_DETALLE_NOMBRE", StringType(), True),
    StructField("ESPECIFICA", StringType(), True),
    StructField("ESPECIFICA_NOMBRE", StringType(), True),
    StructField("ESPECIFICA_DETALLE", StringType(), True),
    StructField("ESPECIFICA_DETALLE_NOMBRE", StringType(), True),
    StructField("MONTO_PIA", DoubleType(), True),
    StructField("MONTO_PIM", DoubleType(), True),
    StructField("MONTO_CERTIFICADO", DoubleType(), True),
    StructField("MONTO_COMPROMETIDO_ANUAL", DoubleType(), True),
    StructField("MONTO_COMPROMETIDO", DoubleType(), True),
    StructField("MONTO_DEVENGADO", DoubleType(), True),
    StructField("MONTO_GIRADO", DoubleType(), True),
])

# Columnas que usamos en el pipeline (subset del schema completo)
COLUMNAS_PIPELINE = [
    "ANO_EJE",
    "MES_EJE",
    "NIVEL_GOBIERNO_NOMBRE",
    "SECTOR_NOMBRE",
    "DEPARTAMENTO_EJECUTORA_NOMBRE",
    "DISTRITO_EJECUTORA_NOMBRE",
    "MONTO_DEVENGADO",
]


def leer_csv_con_schema(
    spark: SparkSession,
    ruta: Path | str,
    *,
    columnas: list[str] | None = None,
) -> DataFrame:
    """Lee un CSV del MEF con schema explicito.

    Parametros
    ----------
    spark : SparkSession
    ruta : Path o str
        Ruta al archivo CSV.
    columnas : list[str], opcional
        Subset de columnas a seleccionar. Por defecto usa COLUMNAS_PIPELINE.

    Returns
    -------
    DataFrame
        DataFrame con las columnas solicitadas.
    """
    ruta = str(ruta)
    columnas = columnas or COLUMNAS_PIPELINE

    logger.info("Leyendo CSV con schema explicito: %s", ruta)

    df = (
        spark.read
        .option("header", "true")
        .option("encoding", "UTF-8")
        .schema(SCHEMA_GASTO_MEF)
        .csv(ruta)
    )

    total = df.count()
    logger.info("Registros leidos: %d", total)

    df_select = df.select(*columnas)
    logger.info("Columnas seleccionadas: %s", columnas)

    return df_select
