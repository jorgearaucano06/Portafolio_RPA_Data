"""
Tests para src/agregacion/transformaciones.py

Usa la fixture df_limpio de conftest.py que contiene 6 filas limpias:
- LIMA: 1000 + 500 = 1500
- CUSCO: 300 + 200 = 500
- AREQUIPA: 600 + 400 = 1000
- EDUCACION: 1000 + 300 + 600 = 1900
- SALUD: 500 + 200 + 400 = 1100

Ejecucion:
    python -m pytest tests/test_agregacion.py -v
"""

from src.agregacion.transformaciones import (
    agregar_por_departamento,
    agregar_por_departamento_sql,
    agregar_por_sector,
)


class TestAgregarPorDepartamento:
    """Tests de agregacion por departamento (DataFrame API)."""

    def test_numero_de_grupos(self, df_limpio):
        """Debe producir 3 grupos: LIMA, CUSCO, AREQUIPA."""
        df_agg = agregar_por_departamento(df_limpio)
        assert df_agg.count() == 3

    def test_columnas_de_salida(self, df_limpio):
        """Verifica que las columnas esperadas estan presentes."""
        df_agg = agregar_por_departamento(df_limpio)
        esperadas = {"departamento", "total_monto", "promedio_monto",
                     "num_registros", "monto_max", "monto_min"}
        assert set(df_agg.columns) == esperadas

    def test_total_lima(self, df_limpio):
        """LIMA: 1000 + 500 = 1500."""
        df_agg = agregar_por_departamento(df_limpio)
        fila = df_agg.filter(df_agg.departamento == "LIMA").collect()[0]
        assert fila["total_monto"] == 1500.0

    def test_total_cusco(self, df_limpio):
        """CUSCO: 300 + 200 = 500."""
        df_agg = agregar_por_departamento(df_limpio)
        fila = df_agg.filter(df_agg.departamento == "CUSCO").collect()[0]
        assert fila["total_monto"] == 500.0

    def test_total_arequipa(self, df_limpio):
        """AREQUIPA: 600 + 400 = 1000."""
        df_agg = agregar_por_departamento(df_limpio)
        fila = df_agg.filter(df_agg.departamento == "AREQUIPA").collect()[0]
        assert fila["total_monto"] == 1000.0

    def test_num_registros_por_grupo(self, df_limpio):
        """Cada departamento tiene 2 registros."""
        df_agg = agregar_por_departamento(df_limpio)
        conteos = {fila["departamento"]: fila["num_registros"]
                   for fila in df_agg.collect()}
        assert all(c == 2 for c in conteos.values())

    def test_orden_descendente(self, df_limpio):
        """El resultado esta ordenado por total_monto DESC."""
        df_agg = agregar_por_departamento(df_limpio)
        totales = [fila["total_monto"] for fila in df_agg.collect()]
        assert totales == sorted(totales, reverse=True)


class TestAgregarPorSector:
    """Tests de agregacion por sector."""

    def test_numero_de_grupos(self, df_limpio):
        """Debe producir 2 grupos: EDUCACION, SALUD."""
        df_agg = agregar_por_sector(df_limpio)
        assert df_agg.count() == 2

    def test_total_educacion(self, df_limpio):
        """EDUCACION: 1000 + 300 + 600 = 1900."""
        df_agg = agregar_por_sector(df_limpio)
        fila = df_agg.filter(df_agg.sector == "EDUCACION").collect()[0]
        assert fila["total_monto"] == 1900.0

    def test_total_salud(self, df_limpio):
        """SALUD: 500 + 200 + 400 = 1100."""
        df_agg = agregar_por_sector(df_limpio)
        fila = df_agg.filter(df_agg.sector == "SALUD").collect()[0]
        assert fila["total_monto"] == 1100.0


class TestAgregarPorDepartamentoSQL:
    """Tests de agregacion SQL (debe dar los mismos resultados que DataFrame API)."""

    def test_sql_coincide_con_dataframe_api(self, spark, df_limpio):
        """El resultado SQL debe coincidir con el de DataFrame API."""
        df_api = agregar_por_departamento(df_limpio)
        df_sql = agregar_por_departamento_sql(spark, df_limpio)

        # Misma cantidad de grupos
        assert df_api.count() == df_sql.count()

        # Mismas columnas
        assert set(df_api.columns) == set(df_sql.columns)

        # Mismos totales por departamento
        totales_api = {f["departamento"]: f["total_monto"] for f in df_api.collect()}
        totales_sql = {f["departamento"]: f["total_monto"] for f in df_sql.collect()}
        assert totales_api == totales_sql
