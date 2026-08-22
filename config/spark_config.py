"""
Factory de SparkSession.

Centraliza toda la configuracion de entorno (JAVA_HOME, HADOOP_HOME, PATH)
y los parametros de SparkSession en un solo lugar. Reemplaza los bloques
os.environ dispersos en los scripts de v1.

Uso:
    from config.spark_config import crear_spark_session
    spark = crear_spark_session()
"""

from __future__ import annotations

import os
import sys

from config.settings import settings


def crear_spark_session(
    app_name: str | None = None,
    master: str | None = None,
) -> "SparkSession":  # noqa: F821 — import diferido
    """Crea y devuelve una SparkSession configurada.

    Parametros
    ----------
    app_name : str, opcional
        Nombre de la aplicacion Spark. Por defecto usa settings.spark.app_name.
    master : str, opcional
        URL del master. Por defecto usa settings.spark.master (local[*]).

    Returns
    -------
    SparkSession
    """
    cfg = settings.spark

    # Variables de entorno — setdefault para no pisar valores ya configurados
    os.environ.setdefault("JAVA_HOME", cfg.java_home)
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ.setdefault("HADOOP_HOME", cfg.hadoop_home)

    hadoop_bin = os.path.join(cfg.hadoop_home, "bin")
    if hadoop_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ["PATH"]

    # Import diferido: evita que el import de config/ dispare la JVM
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder
        .appName(app_name or cfg.app_name)
        .master(master or cfg.master)
        .config("spark.driver.memory", cfg.driver_memory)
        .config("spark.sql.shuffle.partitions", str(cfg.shuffle_partitions))
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    return spark
