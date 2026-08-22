"""
Fase 3 — Filtros de calidad UAT en Spark.

Replica las reglas de calidad de rpa_ingesta.py (v1) usando la API de
DataFrames de Spark. Las reglas son:

1. MONTO_DEVENGADO debe ser > 0 (rechaza 0, negativos y nulls)
2. DISTRITO_EJECUTORA_NOMBRE no puede ser null ni vacio

Uso:
    from src.calidad.filtros_uat import aplicar_filtros_uat

    df_limpio, metricas = aplicar_filtros_uat(df, config.calidad)
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim, when

from config.settings import CalidadConfig
from src.excepciones import CalidadError

logger = logging.getLogger(__name__)


def aplicar_filtros_uat(
    df: DataFrame,
    config: CalidadConfig,
) -> tuple[DataFrame, dict]:
    """Aplica filtros de calidad UAT al DataFrame.

    Parametros
    ----------
    df : DataFrame
        DataFrame con los datos crudos del MEF.
    config : CalidadConfig
        Umbrales de calidad (monto_minimo, umbral_rechazo).

    Returns
    -------
    tuple[DataFrame, dict]
        (df_limpio, metricas) donde metricas contiene conteos y porcentajes.

    Raises
    ------
    CalidadError
        Si el porcentaje de rechazo supera config.umbral_rechazo.
    """
    total = df.count()
    logger.info("Registros de entrada: %d", total)

    # ─── Regla 1: MONTO_DEVENGADO > monto_minimo (default 0) ───
    # Rechaza nulls, ceros y negativos (misma logica que v1)
    filtro_monto = col("MONTO_DEVENGADO").isNotNull() & (
        col("MONTO_DEVENGADO") > config.monto_minimo
    )

    # ─── Regla 2: DISTRITO_EJECUTORA_NOMBRE no vacio ni null ───
    filtro_distrito = col("DISTRITO_EJECUTORA_NOMBRE").isNotNull() & (
        trim(col("DISTRITO_EJECUTORA_NOMBRE")) != ""
    )

    # Columna de diagnostico: motivo de rechazo (para metricas)
    df_diagnostico = df.withColumn(
        "_motivo_rechazo",
        when(~filtro_monto, "monto_invalido")
        .when(~filtro_distrito, "distrito_vacio")
        .otherwise(None),
    )

    # Separar limpios y rechazados
    df_limpio = df_diagnostico.filter(col("_motivo_rechazo").isNull()).drop(
        "_motivo_rechazo"
    )
    df_rechazados = df_diagnostico.filter(col("_motivo_rechazo").isNotNull())

    validos = df_limpio.count()
    rechazados = total - validos

    # Desglose por motivo de rechazo
    desglose = {}
    if rechazados > 0:
        filas_desglose = (
            df_rechazados.groupBy("_motivo_rechazo")
            .count()
            .collect()
        )
        desglose = {fila["_motivo_rechazo"]: fila["count"] for fila in filas_desglose}

    pct_rechazo = rechazados / total if total > 0 else 0.0

    metricas = {
        "total": total,
        "validos": validos,
        "rechazados": rechazados,
        "pct_rechazo": pct_rechazo,
        "desglose": desglose,
    }

    logger.info("Validos: %d | Rechazados: %d (%.1f%%)", validos, rechazados, pct_rechazo * 100)
    for motivo, conteo in desglose.items():
        logger.info("  - %s: %d", motivo, conteo)

    # Abortar si la tasa de rechazo es inaceptable
    if pct_rechazo > config.umbral_rechazo:
        logger.error(
            "Tasa de rechazo %.1f%% supera umbral %.1f%%",
            pct_rechazo * 100,
            config.umbral_rechazo * 100,
        )
        raise CalidadError(pct_rechazo=pct_rechazo, umbral=config.umbral_rechazo)

    return df_limpio, metricas
