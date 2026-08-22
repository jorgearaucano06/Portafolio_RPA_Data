"""
Fase 2 — Descarga HTTP del CSV del MEF.

Descarga el archivo completo con streaming chunked y reintentos
con backoff exponencial. Reemplaza la logica de descarga de rpa_ingesta.py (v1)
con manejo de errores robusto.

Uso:
    from src.ingesta.descarga import descargar_csv

    ruta = descargar_csv(url, destino)  # -> Path al archivo descargado
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import requests

from src.excepciones import DescargaError

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 512_000  # 500 KB por bloque
_MAX_INTENTOS = 3
_BACKOFF_BASE = 2  # segundos: 2, 4, 8
_TIMEOUT = 30  # segundos


def descargar_csv(
    url: str,
    destino: Path,
    *,
    max_intentos: int = _MAX_INTENTOS,
    chunk_size: int = _CHUNK_SIZE,
) -> Path:
    """Descarga un CSV desde una URL a disco con reintentos.

    Parametros
    ----------
    url : str
        URL del archivo CSV.
    destino : Path
        Ruta donde guardar el archivo. Se crean directorios padres si no existen.
    max_intentos : int
        Cantidad maxima de reintentos (default: 3).
    chunk_size : int
        Tamano de cada bloque de descarga en bytes (default: 500 KB).

    Returns
    -------
    Path
        Ruta al archivo descargado.

    Raises
    ------
    DescargaError
        Si la descarga falla tras agotar todos los reintentos.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    ultimo_error = ""

    for intento in range(1, max_intentos + 1):
        try:
            logger.info(
                "Descargando %s (intento %d/%d)...", url, intento, max_intentos
            )
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (MEF-Pipeline-v2)"},
                stream=True,
                timeout=_TIMEOUT,
            )
            response.raise_for_status()

            bytes_descargados = 0
            with open(destino, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        bytes_descargados += len(chunk)

            mb = bytes_descargados / (1024 * 1024)
            logger.info("Descarga completa: %.1f MB -> %s", mb, destino)
            return destino

        except requests.RequestException as e:
            ultimo_error = str(e)
            logger.warning(
                "Intento %d/%d fallido: %s", intento, max_intentos, ultimo_error
            )
            if intento < max_intentos:
                espera = _BACKOFF_BASE ** intento
                logger.info("Reintentando en %d s...", espera)
                time.sleep(espera)

    logger.error("Descarga fallida tras %d intentos: %s", max_intentos, url)
    raise DescargaError(url=url, intentos=max_intentos, ultimo_error=ultimo_error)
