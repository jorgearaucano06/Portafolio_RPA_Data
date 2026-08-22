"""
Fase 3 — Tracking de metricas de calidad.

Registra metricas de calidad en formato JSON para auditoria y tracking.
En Fase 8, estas metricas migraran a MLflow.

Uso:
    from src.calidad.metricas import guardar_metricas_calidad, cargar_metricas_calidad

    guardar_metricas_calidad(metricas, ruta)
    historial = cargar_metricas_calidad(ruta)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def guardar_metricas_calidad(
    metricas: dict[str, Any],
    ruta: Path | str,
) -> Path:
    """Guarda metricas de calidad en un archivo JSON (append).

    Cada ejecucion agrega una entrada al array JSON con timestamp.

    Parametros
    ----------
    metricas : dict
        Diccionario de metricas (output de aplicar_filtros_uat).
    ruta : Path o str
        Ruta al archivo JSON de metricas.

    Returns
    -------
    Path
        Ruta al archivo de metricas.
    """
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # Cargar historial existente o crear nuevo
    historial = []
    if ruta.exists():
        with open(ruta, "r", encoding="utf-8") as f:
            historial = json.load(f)

    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **metricas,
    }
    historial.append(entrada)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2, ensure_ascii=False, default=str)

    logger.info("Metricas de calidad guardadas en %s (%d entradas)", ruta, len(historial))
    return ruta


def cargar_metricas_calidad(ruta: Path | str) -> list[dict[str, Any]]:
    """Carga el historial de metricas de calidad desde JSON.

    Parametros
    ----------
    ruta : Path o str
        Ruta al archivo JSON de metricas.

    Returns
    -------
    list[dict]
        Lista de entradas de metricas, cada una con timestamp.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        logger.warning("No existe archivo de metricas: %s", ruta)
        return []

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)
