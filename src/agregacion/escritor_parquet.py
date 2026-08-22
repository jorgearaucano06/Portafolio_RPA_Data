"""
Fase 4 — Escritura de DataFrames a Parquet particionado.

Escribe el resultado de las agregaciones (o cualquier DataFrame) en formato
Parquet, opcionalmente particionado por columnas. Parquet es columnar y
comprimido — ideal para lecturas analiticas posteriores.

Uso:
    from src.agregacion.escritor_parquet import escribir_parquet

    escribir_parquet(df, ruta, particiones=["ANO_EJE", "DEPARTAMENTO_EJECUTORA_NOMBRE"])
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

logger = logging.getLogger(__name__)


def escribir_parquet(
    df: DataFrame,
    ruta: Path | str,
    *,
    particiones: list[str] | None = None,
    modo: str = "overwrite",
) -> Path:
    """Escribe un DataFrame a Parquet.

    Parametros
    ----------
    df : DataFrame
        DataFrame a escribir.
    ruta : Path o str
        Directorio de salida.
    particiones : list[str], opcional
        Columnas para particionar (e.g. ["ANO_EJE", "DEPARTAMENTO_EJECUTORA_NOMBRE"]).
    modo : str
        Modo de escritura: "overwrite", "append", "error", "ignore".

    Returns
    -------
    Path
        Ruta al directorio Parquet escrito.
    """
    ruta = Path(ruta)
    ruta_str = str(ruta)

    writer = df.write.mode(modo)

    if particiones:
        writer = writer.partitionBy(*particiones)
        logger.info("Escribiendo Parquet particionado por %s -> %s", particiones, ruta)
    else:
        logger.info("Escribiendo Parquet sin particionar -> %s", ruta)

    writer.parquet(ruta_str)

    logger.info("Escritura Parquet completada: %s", ruta)
    return ruta
