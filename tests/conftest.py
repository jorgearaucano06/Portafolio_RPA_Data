"""
Fixtures compartidas para pytest.

Proporciona una SparkSession reutilizable (session-scoped) y DataFrames
de ejemplo con edge cases para testing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# El import de pyspark se hace dentro de las fixtures para evitar
# que la JVM arranque solo por importar conftest.


@pytest.fixture(scope="session")
def spark():
    """SparkSession local[2] compartida entre todos los tests de la sesion.

    Usa local[2] (no local[*]) para detectar bugs de paralelismo
    sin consumir todos los cores de la maquina.
    """
    from config.spark_config import crear_spark_session

    session = crear_spark_session(
        app_name="tests_pipeline_v2",
        master="local[2]",
    )
    yield session
    session.stop()


@pytest.fixture()
def df_sample(spark):
    """DataFrame pequeno con edge cases para tests unitarios.

    Incluye:
    - Filas validas con montos positivos
    - Fila con monto 0 (debe ser rechazada por filtro UAT)
    - Fila con monto negativo (debe ser rechazada)
    - Fila con distrito vacio (debe ser rechazada)
    - Fila con monto muy grande (no debe ser rechazada)
    """
    from pyspark.sql.types import (
        DoubleType,
        StringType,
        StructField,
        StructType,
    )

    schema = StructType([
        StructField("ANO_EJE", StringType(), True),
        StructField("MES_EJE", StringType(), True),
        StructField("NIVEL_GOBIERNO_NOMBRE", StringType(), True),
        StructField("SECTOR_NOMBRE", StringType(), True),
        StructField("DEPARTAMENTO_EJECUTORA_NOMBRE", StringType(), True),
        StructField("DISTRITO_EJECUTORA_NOMBRE", StringType(), True),
        StructField("MONTO_DEVENGADO", DoubleType(), True),
    ])

    datos = [
        ("2020", "01", "GOBIERNO NACIONAL", "EDUCACION", "LIMA", "LIMA", 1500.0),
        ("2020", "02", "GOBIERNO REGIONAL", "SALUD", "CUSCO", "CUSCO", 830.5),
        ("2020", "03", "GOBIERNO LOCAL", "TRANSPORTE", "AREQUIPA", "AREQUIPA", 990.0),
        ("2020", "04", "GOBIERNO NACIONAL", "DEFENSA", "LIMA", "LIMA", 0.0),            # monto = 0
        ("2020", "05", "GOBIERNO REGIONAL", "EDUCACION", "LA LIBERTAD", "TRUJILLO", -50.0),  # negativo
        ("2020", "06", "GOBIERNO LOCAL", "SALUD", "LIMA", "", 200.0),                    # distrito vacio
        ("2020", "07", "GOBIERNO NACIONAL", "INTERIOR", "LIMA", None, 300.0),            # distrito None
        ("2020", "08", "GOBIERNO REGIONAL", "EDUCACION", "PIURA", "PIURA", 9999999.0),  # monto grande
    ]

    return spark.createDataFrame(datos, schema=schema)


@pytest.fixture()
def df_limpio(spark):
    """DataFrame limpio (sin edge cases) para tests de agregacion.

    6 filas validas: 3 departamentos x 2 sectores.
    Montos elegidos para que las sumas sean faciles de verificar.
    """
    from pyspark.sql.types import (
        DoubleType,
        StringType,
        StructField,
        StructType,
    )

    schema = StructType([
        StructField("ANO_EJE", StringType(), True),
        StructField("MES_EJE", StringType(), True),
        StructField("NIVEL_GOBIERNO_NOMBRE", StringType(), True),
        StructField("SECTOR_NOMBRE", StringType(), True),
        StructField("DEPARTAMENTO_EJECUTORA_NOMBRE", StringType(), True),
        StructField("DISTRITO_EJECUTORA_NOMBRE", StringType(), True),
        StructField("MONTO_DEVENGADO", DoubleType(), True),
    ])

    datos = [
        ("2020", "01", "GOBIERNO NACIONAL", "EDUCACION", "LIMA", "LIMA", 1000.0),
        ("2020", "02", "GOBIERNO NACIONAL", "SALUD", "LIMA", "LIMA", 500.0),
        ("2020", "03", "GOBIERNO REGIONAL", "EDUCACION", "CUSCO", "CUSCO", 300.0),
        ("2020", "04", "GOBIERNO REGIONAL", "SALUD", "CUSCO", "CUSCO", 200.0),
        ("2020", "05", "GOBIERNO LOCAL", "EDUCACION", "AREQUIPA", "AREQUIPA", 600.0),
        ("2020", "06", "GOBIERNO LOCAL", "SALUD", "AREQUIPA", "AREQUIPA", 400.0),
    ]

    return spark.createDataFrame(datos, schema=schema)


@pytest.fixture()
def ruta_sample_csv() -> Path:
    """Ruta al CSV de ejemplo con ~50 filas para tests de integracion."""
    return Path(__file__).parent / "data" / "sample_gasto.csv"
