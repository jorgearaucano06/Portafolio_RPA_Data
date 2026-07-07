"""
Fase 0 - Script de verificacion del entorno Spark.
Confirma la cadena completa: Python -> Py4J -> JVM (JDK 17) -> Spark.
"""
import os
import sys

# ─── BLOQUE 1: Variables de entorno ───
# JAVA_HOME: le dice a PySpark que JVM arrancar. setx ya lo grabo en Windows,
# pero lo fijamos aqui tambien para que el script funcione en terminales viejas.
os.environ.setdefault("JAVA_HOME", r"C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot")

# PYSPARK_PYTHON: obliga a que los procesos worker de Spark usen el MISMO
# Python del venv que ejecuta este script. Sin esto, en Windows Spark puede
# intentar lanzar otro Python del sistema y fallar con errores cripticos.
os.environ["PYSPARK_PYTHON"] = sys.executable

# HADOOP_HOME: Spark delega la E/S de archivos en las librerias de Hadoop.
# En Windows, Hadoop necesita binarios nativos (winutils.exe + hadoop.dll)
# que Apache no distribuye oficialmente. Sin esto: error al escribir Parquet.
os.environ.setdefault("HADOOP_HOME", r"C:\hadoop")
# La JVM localiza hadoop.dll a traves del PATH del proceso:
os.environ["PATH"] = r"C:\hadoop\bin;" + os.environ["PATH"]

from pyspark.sql import SparkSession

# ─── BLOQUE 2: SparkSession ───
# SparkSession = punto de entrada a Spark (lo estudiaremos a fondo en Fase 1).
# master("local[*]") = modo local usando TODOS los cores de esta maquina.
# El [*] es literal: local[4] usaria 4 cores, local[*] usa todos.
spark = (
    SparkSession.builder
    .appName("verificacion_setup_v2")
    .master("local[*]")
    .getOrCreate()
)

print("=" * 50)
print(f"Version de Spark  : {spark.version}")
print(f"Cores disponibles : {spark.sparkContext.defaultParallelism}")
print(f"Python del driver : {sys.executable}")
print("=" * 50)

# ─── BLOQUE 3: DataFrame minimo ───
# Creamos un DataFrame de juguete y forzamos su materializacion con .show()
# (una 'accion' -- concepto clave de Fase 1).
df = spark.createDataFrame(
    [("LIMA", 1500.0), ("CUSCO", 830.5), ("AREQUIPA", 990.0)],
    schema=["departamento", "monto"],
)
df.show()

# ─── BLOQUE 4: Prueba de escritura en disco ───
# En Windows, Spark a veces necesita utilidades nativas de Hadoop (winutils)
# para escribir archivos. Lo probamos AHORA para no descubrirlo en Fase 4.
salida = "data/tmp_verificacion_parquet"
df.write.mode("overwrite").parquet(salida)
print(f"Escritura Parquet OK -> {salida}")

spark.stop()
print("VERIFICACION COMPLETA: el entorno esta listo para la Fase 1.")
