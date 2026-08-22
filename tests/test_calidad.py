"""
Tests para src/calidad/filtros_uat.py

Usa la fixture df_sample de conftest.py que contiene 8 filas:
- 3 validas normales (LIMA, CUSCO, AREQUIPA)
- 1 con monto = 0 (rechazar)
- 1 con monto negativo (rechazar)
- 1 con distrito vacio "" (rechazar)
- 1 con distrito None (rechazar)
- 1 con monto grande (aceptar)

Ejecucion:
    python -m pytest tests/test_calidad.py -v
"""

import pytest

from config.settings import CalidadConfig
from src.calidad.filtros_uat import aplicar_filtros_uat
from src.excepciones import CalidadError


class TestFiltrosUAT:
    """Tests de los filtros de calidad UAT."""

    def test_rechaza_monto_cero(self, df_sample):
        """Monto = 0 debe ser rechazado."""
        config = CalidadConfig()
        df_limpio, metricas = aplicar_filtros_uat(df_sample, config)

        montos = [fila["MONTO_DEVENGADO"] for fila in df_limpio.collect()]
        assert 0.0 not in montos

    def test_rechaza_monto_negativo(self, df_sample):
        """Monto negativo debe ser rechazado."""
        config = CalidadConfig()
        df_limpio, _ = aplicar_filtros_uat(df_sample, config)

        montos = [fila["MONTO_DEVENGADO"] for fila in df_limpio.collect()]
        assert all(m > 0 for m in montos)

    def test_rechaza_distrito_vacio(self, df_sample):
        """Distrito vacio '' debe ser rechazado."""
        config = CalidadConfig()
        df_limpio, _ = aplicar_filtros_uat(df_sample, config)

        distritos = [fila["DISTRITO_EJECUTORA_NOMBRE"] for fila in df_limpio.collect()]
        assert "" not in distritos

    def test_rechaza_distrito_none(self, df_sample):
        """Distrito None debe ser rechazado."""
        config = CalidadConfig()
        df_limpio, _ = aplicar_filtros_uat(df_sample, config)

        distritos = [fila["DISTRITO_EJECUTORA_NOMBRE"] for fila in df_limpio.collect()]
        assert None not in distritos

    def test_acepta_monto_grande(self, df_sample):
        """Monto grande (9999999) debe ser aceptado."""
        config = CalidadConfig()
        df_limpio, _ = aplicar_filtros_uat(df_sample, config)

        montos = [fila["MONTO_DEVENGADO"] for fila in df_limpio.collect()]
        assert 9999999.0 in montos

    def test_conteo_validos(self, df_sample):
        """De 8 filas: 4 validas (LIMA, CUSCO, AREQUIPA, PIURA)."""
        config = CalidadConfig()
        df_limpio, metricas = aplicar_filtros_uat(df_sample, config)

        assert metricas["total"] == 8
        assert metricas["validos"] == 4
        assert metricas["rechazados"] == 4

    def test_metricas_desglose(self, df_sample):
        """Las metricas incluyen desglose por motivo de rechazo."""
        config = CalidadConfig()
        _, metricas = aplicar_filtros_uat(df_sample, config)

        assert "desglose" in metricas
        assert "monto_invalido" in metricas["desglose"]
        assert "distrito_vacio" in metricas["desglose"]

    def test_calidad_error_umbral_bajo(self, df_sample):
        """Lanza CalidadError si pct_rechazo > umbral."""
        # Con 4/8 rechazados = 50%, un umbral de 10% debe fallar
        config = CalidadConfig(umbral_rechazo=0.10)

        with pytest.raises(CalidadError) as exc_info:
            aplicar_filtros_uat(df_sample, config)

        assert exc_info.value.pct_rechazo == 0.5
        assert exc_info.value.umbral == 0.10

    def test_no_lanza_error_umbral_alto(self, df_sample):
        """No lanza CalidadError si pct_rechazo <= umbral."""
        # 50% rechazo con umbral 60% -> no debe fallar
        config = CalidadConfig(umbral_rechazo=0.60)
        df_limpio, metricas = aplicar_filtros_uat(df_sample, config)

        assert metricas["validos"] == 4
