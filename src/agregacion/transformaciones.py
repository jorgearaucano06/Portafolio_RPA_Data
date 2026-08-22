"""
Fase 4 — Agregaciones con Spark.

Agrupa datos limpios por departamento y sector, calcula metricas
de gasto (total, promedio, conteo, max, min).

Dos interfaces equivalentes: DataFrame API y Spark SQL.

Uso:
    from src.agregacion.transformaciones import agregar_por_departamento, agregar_por_sector

    df_dept = agregar_por_departamento(df_limpio)
    df_sect = agregar_por_sector(df_limpio)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)


def agregar_por_departamento(df: DataFrame) -> DataFrame:
    """Agrega gasto por departamento usando DataFrame API.

    Parametros
    ----------
    df : DataFrame
        DataFrame limpio (post-filtros UAT). Debe tener las columnas
        DEPARTAMENTO_EJECUTORA_NOMBRE y MONTO_DEVENGADO.

    Returns
    -------
    DataFrame
        Columnas: departamento, total_monto, promedio_monto, num_registros,
        monto_max, monto_min. Ordenado por total_monto DESC.
    """
    from pyspark.sql import functions as F

    df_agg = (
        df.groupBy(F.col("DEPARTAMENTO_EJECUTORA_NOMBRE").alias("departamento"))
        .agg(
            F.sum("MONTO_DEVENGADO").alias("total_monto"),
            F.avg("MONTO_DEVENGADO").alias("promedio_monto"),
            F.count("MONTO_DEVENGADO").alias("num_registros"),
            F.max("MONTO_DEVENGADO").alias("monto_max"),
            F.min("MONTO_DEVENGADO").alias("monto_min"),
        )
        .orderBy(F.col("total_monto").desc())
    )

    n = df_agg.count()
    logger.info("Agregacion por departamento: %d grupos", n)
    return df_agg


def agregar_por_sector(df: DataFrame) -> DataFrame:
    """Agrega gasto por sector usando DataFrame API.

    Parametros
    ----------
    df : DataFrame
        DataFrame limpio con columnas SECTOR_NOMBRE y MONTO_DEVENGADO.

    Returns
    -------
    DataFrame
        Columnas: sector, total_monto, promedio_monto, num_registros.
        Ordenado por total_monto DESC.
    """
    from pyspark.sql import functions as F

    df_agg = (
        df.groupBy(F.col("SECTOR_NOMBRE").alias("sector"))
        .agg(
            F.sum("MONTO_DEVENGADO").alias("total_monto"),
            F.avg("MONTO_DEVENGADO").alias("promedio_monto"),
            F.count("MONTO_DEVENGADO").alias("num_registros"),
        )
        .orderBy(F.col("total_monto").desc())
    )

    n = df_agg.count()
    logger.info("Agregacion por sector: %d grupos", n)
    return df_agg


def agregar_por_departamento_sql(
    spark: SparkSession,
    df: DataFrame,
    nombre_vista: str = "gastos_limpios",
) -> DataFrame:
    """Misma agregacion por departamento pero con Spark SQL.

    Parametros
    ----------
    spark : SparkSession
    df : DataFrame
    nombre_vista : str
        Nombre de la vista temporal para la consulta SQL.

    Returns
    -------
    DataFrame
    """
    df.createOrReplaceTempView(nombre_vista)

    df_sql = spark.sql(f"""
        SELECT
            DEPARTAMENTO_EJECUTORA_NOMBRE AS departamento,
            SUM(MONTO_DEVENGADO)   AS total_monto,
            AVG(MONTO_DEVENGADO)   AS promedio_monto,
            COUNT(MONTO_DEVENGADO) AS num_registros,
            MAX(MONTO_DEVENGADO)   AS monto_max,
            MIN(MONTO_DEVENGADO)   AS monto_min
        FROM {nombre_vista}
        GROUP BY DEPARTAMENTO_EJECUTORA_NOMBRE
        ORDER BY total_monto DESC
    """)

    logger.info("Agregacion SQL por departamento completada")
    return df_sql
