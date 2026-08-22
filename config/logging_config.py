"""
Configuracion de logging para todo el proyecto.

Llamar setup_logging() una sola vez al inicio del proceso (main, notebook, test).
Despues, cada modulo usa:

    import logging
    logger = logging.getLogger(__name__)
    logger.info("mensaje")

Formato de salida:
    2026-08-22 14:30:15 | src.ingesta.descarga | INFO | mensaje
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_CONFIGURADO = False

_FORMATO = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
_FECHA = "%Y-%m-%d %H:%M:%S"

# Loggers ruidosos que queremos silenciar
_LOGGERS_SILENCIADOS = [
    "py4j",
    "py4j.java_gateway",
    "pyspark",
    "org.apache.spark",
]


def setup_logging(
    nivel: int = logging.INFO,
    archivo: Path | str | None = None,
) -> None:
    """Configura el logging del proyecto.

    Parametros
    ----------
    nivel : int
        Nivel minimo de logging (default: INFO).
    archivo : Path o str, opcional
        Si se proporciona, ademas de consola se escribe a este archivo.
    """
    global _CONFIGURADO
    if _CONFIGURADO:
        return
    _CONFIGURADO = True

    formatter = logging.Formatter(_FORMATO, datefmt=_FECHA)

    # Handler de consola
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    handlers: list[logging.Handler] = [console]

    # Handler de archivo (opcional)
    if archivo is not None:
        ruta = Path(archivo)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(ruta, encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configurar root logger
    root = logging.getLogger()
    root.setLevel(nivel)
    for h in handlers:
        root.addHandler(h)

    # Silenciar loggers ruidosos
    for nombre in _LOGGERS_SILENCIADOS:
        logging.getLogger(nombre).setLevel(logging.WARNING)
