"""
Fase 0 — Verificacion del entorno Spark.

Confirma la cadena completa: Python -> Py4J -> JVM (JDK 17) -> Spark.
Refactorizado para usar config/ centralizado (v2).
"""

import logging
import sys

from config.logging_config import setup_logging
from config.spark_config import crear_spark_session

setup_logging()
logger = logging.getLogger(__name__)

# ─── SparkSession via factory centralizada ───
# Toda la config de JAVA_HOME, HADOOP_HOME, PATH, driver.memory
# ahora vive en config/spark_config.py y config/settings.py.
spark = crear_spark_session(app_name="verificacion_setup_v2")

logger.info("=" * 50)
logger.info("Version de Spark  : %s", spark.version)
logger.info("Cores disponibles : %d", spark.sparkContext.defaultParallelism)
logger.info("Python del driver : %s", sys.executable)
logger.info("=" * 50)

# ─── DataFrame minimo ───
# Creamos un DataFrame de juguete y forzamos su materializacion con .show()
# (una 'accion' — concepto clave de Fase 1).
df = spark.createDataFrame(
    [("LIMA", 1500.0), ("CUSCO", 830.5), ("AREQUIPA", 990.0)],
    schema=["departamento", "monto"],
)
df.show()

# ─── Prueba de escritura en disco ───
# Verifica que winutils.exe + hadoop.dll funcionan para E/S de archivos.
salida = "data/tmp_verificacion_parquet"
df.write.mode("overwrite").parquet(salida)
logger.info("Escritura Parquet OK -> %s", salida)

spark.stop()
logger.info("VERIFICACION COMPLETA: el entorno esta listo para la Fase 1.")
