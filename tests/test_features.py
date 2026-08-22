"""
Tests para src/ml/features.py

Verifica que el feature engineering genera las estructuras correctas
tanto para regresion (por registro) como para clustering (por grupo).

Ejecucion:
    python -m pytest tests/test_features.py -v
"""

import pandas as pd
import numpy as np

from src.ml.features import preparar_features_registro, preparar_features_clustering


def _crear_df_ejemplo() -> pd.DataFrame:
    """DataFrame pandas de ejemplo para tests de features."""
    return pd.DataFrame({
        "ANO_EJE": ["2020"] * 8,
        "MES_EJE": ["01", "02", "03", "04", "01", "02", "03", "04"],
        "NIVEL_GOBIERNO_NOMBRE": [
            "GOBIERNO NACIONAL", "GOBIERNO REGIONAL", "GOBIERNO LOCAL",
            "GOBIERNO NACIONAL", "GOBIERNO REGIONAL", "GOBIERNO LOCAL",
            "GOBIERNO NACIONAL", "GOBIERNO REGIONAL",
        ],
        "SECTOR_NOMBRE": [
            "EDUCACION", "SALUD", "EDUCACION", "SALUD",
            "EDUCACION", "SALUD", "EDUCACION", "SALUD",
        ],
        "DEPARTAMENTO_EJECUTORA_NOMBRE": [
            "LIMA", "CUSCO", "AREQUIPA", "LIMA",
            "CUSCO", "AREQUIPA", "LIMA", "CUSCO",
        ],
        "DISTRITO_EJECUTORA_NOMBRE": [
            "LIMA", "CUSCO", "AREQUIPA", "LIMA",
            "CUSCO", "AREQUIPA", "LIMA", "CUSCO",
        ],
        "MONTO_DEVENGADO": [
            1000.0, 500.0, 300.0, 800.0,
            600.0, 400.0, 1200.0, 700.0,
        ],
    })


class TestFeaturesRegistro:
    """Tests de preparar_features_registro."""

    def test_output_shapes(self):
        """X e y deben tener la misma cantidad de filas."""
        df = _crear_df_ejemplo()
        X, y, nombres = preparar_features_registro(df)

        assert len(X) == len(y) == len(df)

    def test_target_es_monto(self):
        """El target por defecto es MONTO_DEVENGADO."""
        df = _crear_df_ejemplo()
        _, y, _ = preparar_features_registro(df)

        assert list(y) == list(df["MONTO_DEVENGADO"])

    def test_features_son_numericas(self):
        """Todas las features deben ser numericas (post encoding)."""
        df = _crear_df_ejemplo()
        X, _, _ = preparar_features_registro(df)

        assert all(X[col].dtype in [np.int64, np.float64, np.int32,
                                     np.uint8, int] for col in X.columns)

    def test_nombres_coinciden(self):
        """Los nombres devueltos deben ser las columnas de X."""
        df = _crear_df_ejemplo()
        X, _, nombres = preparar_features_registro(df)

        assert nombres == list(X.columns)

    def test_sin_columna_target_en_features(self):
        """MONTO_DEVENGADO no debe aparecer en X."""
        df = _crear_df_ejemplo()
        X, _, _ = preparar_features_registro(df)

        assert "MONTO_DEVENGADO" not in X.columns


class TestFeaturesClustering:
    """Tests de preparar_features_clustering."""

    def test_agrupacion_genera_menos_filas(self):
        """El resultado debe tener menos filas que el original."""
        df = _crear_df_ejemplo()
        df_feat, df_info = preparar_features_clustering(df)

        assert len(df_feat) < len(df)

    def test_features_esperadas(self):
        """Debe generar las metricas agregadas esperadas."""
        df = _crear_df_ejemplo()
        df_feat, _ = preparar_features_clustering(df)

        esperadas = {"total_monto", "promedio_monto", "mediana_monto",
                     "std_monto", "num_registros", "monto_min", "monto_max",
                     "cv_monto", "rango_monto"}
        assert set(df_feat.columns) == esperadas

    def test_sin_nans_en_std(self):
        """std_monto no debe tener NaN (rellenado con 0)."""
        df = _crear_df_ejemplo()
        df_feat, _ = preparar_features_clustering(df)

        assert df_feat["std_monto"].isna().sum() == 0

    def test_info_tiene_etiquetas(self):
        """df_info debe contener las columnas de agrupacion."""
        df = _crear_df_ejemplo()
        _, df_info = preparar_features_clustering(df)

        assert "DEPARTAMENTO_EJECUTORA_NOMBRE" in df_info.columns

    def test_rango_es_correcto(self):
        """rango_monto = monto_max - monto_min."""
        df = _crear_df_ejemplo()
        df_feat, _ = preparar_features_clustering(df)

        rangos_calculados = df_feat["monto_max"] - df_feat["monto_min"]
        pd.testing.assert_series_equal(
            df_feat["rango_monto"].reset_index(drop=True),
            rangos_calculados.reset_index(drop=True),
            check_names=False,
        )
