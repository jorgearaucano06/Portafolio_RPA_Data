"""
Configuracion centralizada con dataclasses inmutables.

Cada seccion del proyecto tiene su propia dataclass (frozen=True).
Los valores por defecto son visibles en el codigo; se pueden sobreescribir
con variables de entorno para adaptarse a otros equipos o a Databricks.

Uso:
    from config.settings import settings
    print(settings.data.url_gasto_mef)
    print(settings.spark.driver_memory)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Raiz del proyecto: dos niveles arriba de este archivo (config/settings.py -> raiz)
_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class DataConfig:
    """Rutas y URLs de datos."""

    url_gasto_mef: str = (
        "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2020-Gasto.csv"
    )
    dir_raw: Path = field(default_factory=lambda: _ROOT / "data" / "raw")
    dir_processed: Path = field(default_factory=lambda: _ROOT / "data" / "processed")
    archivo_csv: str = "gasto_2020.csv"

    @property
    def ruta_csv_raw(self) -> Path:
        return self.dir_raw / self.archivo_csv


@dataclass(frozen=True)
class SparkConfig:
    """Parametros de SparkSession."""

    app_name: str = "mef_pipeline_v2"
    master: str = "local[*]"
    driver_memory: str = field(
        default_factory=lambda: os.getenv("SPARK_DRIVER_MEMORY", "4g")
    )
    shuffle_partitions: int = field(
        default_factory=lambda: int(os.getenv("SPARK_SHUFFLE_PARTITIONS", "8"))
    )
    java_home: str = field(
        default_factory=lambda: os.getenv(
            "JAVA_HOME",
            r"C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot",
        )
    )
    hadoop_home: str = field(
        default_factory=lambda: os.getenv("HADOOP_HOME", r"C:\hadoop")
    )


@dataclass(frozen=True)
class CalidadConfig:
    """Umbrales para filtros de calidad UAT."""

    monto_minimo: float = 0.0
    umbral_rechazo: float = 0.5  # maximo 50% de rechazo antes de abortar
    campos_obligatorios: tuple[str, ...] = (
        "DISTRITO_EJECUTORA_NOMBRE",
        "MONTO_DEVENGADO",
    )


@dataclass(frozen=True)
class MLConfig:
    """Configuracion de modelos y tracking."""

    dir_modelos: Path = field(default_factory=lambda: _ROOT / "models")
    dir_metricas: Path = field(default_factory=lambda: _ROOT / "models" / "metricas")
    test_size: float = 0.2
    random_state: int = 42
    formato_serializacion: str = "joblib"


@dataclass(frozen=True)
class Settings:
    """Contenedor principal — punto de acceso unico a toda la config."""

    data: DataConfig = field(default_factory=DataConfig)
    spark: SparkConfig = field(default_factory=SparkConfig)
    calidad: CalidadConfig = field(default_factory=CalidadConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    root: Path = _ROOT


# Singleton importable: `from config.settings import settings`
settings = Settings()
