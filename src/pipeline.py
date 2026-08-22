"""
Runner del pipeline v2.

Encadena etapas secuencialmente. Cada etapa recibe un DataFrame de Spark
(o None para la primera) y devuelve un DataFrame transformado junto con
un StageResult que registra metricas.

Uso:
    from config import crear_spark_session, setup_logging, settings
    from src.pipeline import ejecutar_pipeline

    setup_logging()
    spark = crear_spark_session()
    resultados = ejecutar_pipeline(spark, settings, etapas=[...])
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

from config.settings import Settings

logger = logging.getLogger(__name__)

# Tipo de una funcion-etapa del pipeline:
#   (spark, df_entrada, config) -> (df_salida, dict_metricas_extra)
# Definido como string para evitar importar pyspark al cargar el modulo.
EtapaFn = Callable[..., Any]


@dataclass
class StageResult:
    """Resultado de una etapa del pipeline."""

    nombre: str
    registros_entrada: int
    registros_salida: int
    tiempo_segundos: float
    metricas: dict[str, Any] = field(default_factory=dict)

    def resumen(self) -> str:
        delta = self.registros_salida - self.registros_entrada
        signo = "+" if delta >= 0 else ""
        return (
            f"{self.nombre:.<30s} "
            f"entrada={self.registros_entrada:>8,d}  "
            f"salida={self.registros_salida:>8,d}  "
            f"({signo}{delta:,d})  "
            f"{self.tiempo_segundos:.2f}s"
        )


def ejecutar_pipeline(
    spark: SparkSession,
    config: Settings,
    etapas: list[tuple[str, EtapaFn]],
) -> list[StageResult]:
    """Ejecuta las etapas del pipeline en secuencia.

    Parametros
    ----------
    spark : SparkSession
    config : Settings
    etapas : lista de tuplas (nombre, funcion_etapa)
        Cada funcion recibe (spark, df, config) y devuelve (df, metricas).

    Returns
    -------
    list[StageResult]
    """
    resultados: list[StageResult] = []
    df: DataFrame | None = None

    logger.info("=" * 60)
    logger.info("INICIO DEL PIPELINE")
    logger.info("=" * 60)

    for nombre, fn in etapas:
        logger.info("Etapa: %s", nombre)
        registros_entrada = df.count() if df is not None else 0

        t0 = time.perf_counter()
        df, metricas = fn(spark, df, config)
        elapsed = time.perf_counter() - t0

        registros_salida = df.count() if df is not None else 0

        resultado = StageResult(
            nombre=nombre,
            registros_entrada=registros_entrada,
            registros_salida=registros_salida,
            tiempo_segundos=elapsed,
            metricas=metricas,
        )
        resultados.append(resultado)
        logger.info(resultado.resumen())

    # Resumen final
    logger.info("=" * 60)
    logger.info("RESUMEN DEL PIPELINE")
    logger.info("=" * 60)
    for r in resultados:
        logger.info(r.resumen())

    tiempo_total = sum(r.tiempo_segundos for r in resultados)
    logger.info("Tiempo total: %.2f s", tiempo_total)
    logger.info("=" * 60)

    return resultados
