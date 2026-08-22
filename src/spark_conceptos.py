"""
Fase 1 — Conceptos fundamentales de Apache Spark.

Este script demuestra los pilares de Spark que se usaran en todo el pipeline v2:

1. SparkSession: punto de entrada, configuracion, ciclo de vida
2. Lazy evaluation: transformaciones (perezosas) vs acciones (ejecutan)
3. Plan de ejecucion: explain() para entender que hara Spark
4. Particiones: como Spark distribuye los datos entre cores
5. Cache: persistir DataFrames en memoria para reusar

Se ejecuta como script independiente:
    python -m src.spark_conceptos
"""

import logging
import time

from config.logging_config import setup_logging
from config.spark_config import crear_spark_session
from config.settings import settings

setup_logging()
logger = logging.getLogger(__name__)


def demostrar_sparksession(spark):
    """SparkSession: punto de entrada unico a Spark."""
    logger.info("=" * 60)
    logger.info("1. SPARKSESSION")
    logger.info("=" * 60)

    logger.info("Version de Spark     : %s", spark.version)
    logger.info("App name             : %s", spark.sparkContext.appName)
    logger.info("Master               : %s", spark.sparkContext.master)
    logger.info("Cores (paralelismo)  : %d", spark.sparkContext.defaultParallelism)
    logger.info("Driver memory        : %s", settings.spark.driver_memory)
    logger.info("Shuffle partitions   : %d", settings.spark.shuffle_partitions)

    # SparkSession sigue el patron singleton: getOrCreate() devuelve la misma
    # instancia si ya existe. Esto evita conflictos de multiples JVM.
    spark2 = crear_spark_session(app_name="otra_app")
    logger.info("Misma instancia?     : %s", spark is spark2)


def demostrar_lazy_evaluation(spark):
    """Lazy evaluation: transformaciones no se ejecutan hasta una accion."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("2. LAZY EVALUATION")
    logger.info("=" * 60)

    # Crear un DataFrame con datos de ejemplo
    datos = [
        ("LIMA", "EDUCACION", 1500.0),
        ("CUSCO", "SALUD", 830.5),
        ("AREQUIPA", "TRANSPORTE", 990.0),
        ("LIMA", "SALUD", 2100.0),
        ("CUSCO", "EDUCACION", 1200.0),
        ("AREQUIPA", "EDUCACION", 680.0),
        ("LIMA", "TRANSPORTE", 3500.0),
        ("PIURA", "EDUCACION", 450.0),
        ("TRUJILLO", "SALUD", 1800.0),
        ("PIURA", "SALUD", 920.0),
    ]
    df = spark.createDataFrame(datos, schema=["departamento", "sector", "monto"])
    logger.info("DataFrame creado con %d filas", len(datos))

    # ─── TRANSFORMACIONES (lazy — no se ejecutan todavia) ───
    # Spark solo registra el plan; no toca los datos aun.
    logger.info("")
    logger.info("Aplicando transformaciones (lazy, no ejecutan nada)...")

    t0 = time.perf_counter()

    # filter(): seleccionar filas que cumplen condicion
    df_filtrado = df.filter(df.monto > 500)

    # select(): elegir columnas
    df_seleccion = df_filtrado.select("departamento", "monto")

    # withColumn(): agregar/modificar columna
    from pyspark.sql.functions import col, upper
    df_transformado = df_seleccion.withColumn(
        "departamento", upper(col("departamento"))
    )

    # orderBy(): ordenar
    df_ordenado = df_transformado.orderBy(col("monto").desc())

    t_lazy = time.perf_counter() - t0
    logger.info("Transformaciones registradas en %.4f s (no tocaron datos)", t_lazy)

    # ─── ACCIONES (eager — ejecutan todo el plan) ───
    logger.info("")
    logger.info("Ejecutando acciones (ahora SI procesa los datos)...")

    # .count() es una accion: fuerza la ejecucion de TODAS las transformaciones
    t0 = time.perf_counter()
    n = df_ordenado.count()
    t_count = time.perf_counter() - t0
    logger.info("count() = %d registros, ejecutado en %.4f s", n, t_count)

    # .show() es una accion: materializa y muestra las primeras filas
    t0 = time.perf_counter()
    df_ordenado.show(5, truncate=False)
    t_show = time.perf_counter() - t0
    logger.info("show() ejecutado en %.4f s", t_show)

    # .collect() es una accion: trae TODO al driver (cuidado con datasets grandes)
    t0 = time.perf_counter()
    filas = df_ordenado.collect()
    t_collect = time.perf_counter() - t0
    logger.info("collect() trajo %d filas al driver en %.4f s", len(filas), t_collect)

    return df, df_ordenado


def demostrar_explain(df_ordenado):
    """explain(): visualizar el plan de ejecucion de Spark."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("3. PLAN DE EJECUCION (explain)")
    logger.info("=" * 60)

    # explain(True) muestra el plan completo:
    # - Parsed Logical Plan: lo que escribio el programador
    # - Analyzed Logical Plan: resuelve nombres de columnas
    # - Optimized Logical Plan: Catalyst aplica optimizaciones
    # - Physical Plan: como Spark realmente ejecutara (shuffles, scans, etc.)
    logger.info("Plan de ejecucion para el DataFrame transformado:")
    df_ordenado.explain(True)


def demostrar_particiones(spark, df):
    """Particiones: como Spark divide los datos para procesar en paralelo."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("4. PARTICIONES")
    logger.info("=" * 60)

    logger.info("Particiones del DataFrame: %d", df.rdd.getNumPartitions())
    logger.info("Paralelismo default: %d", spark.sparkContext.defaultParallelism)

    # repartition(): redistribuir en N particiones (shuffle completo)
    df_repart = df.repartition(4)
    logger.info("Despues de repartition(4): %d particiones", df_repart.rdd.getNumPartitions())

    # coalesce(): reducir particiones SIN shuffle (mas eficiente que repartition)
    df_coalesce = df_repart.coalesce(2)
    logger.info("Despues de coalesce(2): %d particiones", df_coalesce.rdd.getNumPartitions())


def demostrar_cache(df):
    """Cache: persistir un DataFrame en memoria para reusar."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("5. CACHE Y PERSISTENCIA")
    logger.info("=" * 60)

    # Sin cache: cada accion re-ejecuta TODAS las transformaciones
    # Con cache: la primera accion ejecuta y guarda; las siguientes leen de RAM

    df_cached = df.cache()

    # Primera accion: ejecuta + guarda en memoria
    t0 = time.perf_counter()
    df_cached.count()
    t_primera = time.perf_counter() - t0
    logger.info("Primera accion (ejecuta + cachea): %.4f s", t_primera)

    # Segunda accion: lee directamente de RAM
    t0 = time.perf_counter()
    df_cached.count()
    t_segunda = time.perf_counter() - t0
    logger.info("Segunda accion (lee de cache):     %.4f s", t_segunda)

    # Liberar cache cuando ya no se necesita
    df_cached.unpersist()
    logger.info("Cache liberado con unpersist()")


def demostrar_agregaciones_basicas(spark, df):
    """Agregaciones: groupBy + funciones de agregacion."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("6. AGREGACIONES BASICAS")
    logger.info("=" * 60)

    from pyspark.sql import functions as F

    # groupBy + agg: agrupar por departamento y calcular metricas
    df_agg = (
        df.groupBy("departamento")
        .agg(
            F.sum("monto").alias("total_monto"),
            F.avg("monto").alias("promedio_monto"),
            F.count("monto").alias("num_registros"),
        )
        .orderBy(F.col("total_monto").desc())
    )

    logger.info("Gasto por departamento:")
    df_agg.show(truncate=False)

    # Spark SQL: la misma consulta con sintaxis SQL
    df.createOrReplaceTempView("gastos")
    df_sql = spark.sql("""
        SELECT departamento,
               SUM(monto) AS total_monto,
               AVG(monto) AS promedio_monto,
               COUNT(monto) AS num_registros
        FROM gastos
        GROUP BY departamento
        ORDER BY total_monto DESC
    """)
    logger.info("Misma consulta via Spark SQL:")
    df_sql.show(truncate=False)


def main():
    """Punto de entrada: ejecuta todas las demostraciones."""
    spark = crear_spark_session(app_name="spark_conceptos_fase1")

    logger.info("")
    logger.info("*" * 60)
    logger.info("  FASE 1 — CONCEPTOS FUNDAMENTALES DE SPARK")
    logger.info("*" * 60)

    demostrar_sparksession(spark)
    df, df_ordenado = demostrar_lazy_evaluation(spark)
    demostrar_explain(df_ordenado)
    demostrar_particiones(spark, df)
    demostrar_cache(df)
    demostrar_agregaciones_basicas(spark, df)

    spark.stop()
    logger.info("")
    logger.info("FASE 1 COMPLETADA.")


if __name__ == "__main__":
    main()
