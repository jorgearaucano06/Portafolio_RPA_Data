"""
Excepciones custom del pipeline v2.

Jerarquia:
    PipelineError          (base — cualquier fallo del pipeline)
    ├── DescargaError      (HTTP fallo tras reintentos)
    └── CalidadError       (tasa de rechazo inaceptable)

Uso:
    from src.excepciones import DescargaError, CalidadError

    raise DescargaError(
        url="https://...",
        intentos=3,
        ultimo_error="Connection timed out",
    )
"""

from __future__ import annotations


class PipelineError(Exception):
    """Error base del pipeline. Todas las excepciones custom heredan de esta."""

    def __init__(self, stage: str, message: str, detail: str = "") -> None:
        self.stage = stage
        self.message = message
        self.detail = detail
        super().__init__(f"[{stage}] {message}" + (f" — {detail}" if detail else ""))


class DescargaError(PipelineError):
    """La descarga HTTP fallo despues de agotar todos los reintentos."""

    def __init__(self, url: str, intentos: int, ultimo_error: str) -> None:
        self.url = url
        self.intentos = intentos
        self.ultimo_error = ultimo_error
        super().__init__(
            stage="ingesta.descarga",
            message=f"Descarga fallida tras {intentos} intentos: {url}",
            detail=ultimo_error,
        )


class CalidadError(PipelineError):
    """La tasa de rechazo supera el umbral configurado."""

    def __init__(self, pct_rechazo: float, umbral: float) -> None:
        self.pct_rechazo = pct_rechazo
        self.umbral = umbral
        super().__init__(
            stage="calidad",
            message=(
                f"Tasa de rechazo {pct_rechazo:.1%} supera "
                f"el umbral permitido ({umbral:.1%})"
            ),
        )
