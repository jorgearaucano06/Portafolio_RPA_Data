# Checklist de progreso — Portafolio RPA & Data

> Referencia rápida para retomar el trabajo si se corta la sesión.
> Marcar con `[x]` cada paso completado. Actualizar la línea "Último avance".

**Último avance**: Fases 0-4 (código) completadas. Pendiente: ejecutar tests con Spark, commit.
**Rama activa**: `feature/spark-setup`
**Plan completo**: `docs/plan_v2.md`

---

## Infraestructura v2 [COMPLETADA]

- [x] Crear `config/settings.py` — dataclasses frozen con toda la config
- [x] Crear `config/spark_config.py` — factory de SparkSession
- [x] Crear `config/logging_config.py` — logging profesional (stdlib)
- [x] Crear `src/__init__.py` y subpaquetes (ingesta/, calidad/, agregacion/, ml/)
- [x] Crear `src/excepciones.py` — PipelineError, DescargaError, CalidadError
- [x] Crear `src/pipeline.py` — StageResult + ejecutar_pipeline()
- [x] Crear `tests/conftest.py` — fixtures SparkSession + df_sample + df_limpio
- [x] Crear `tests/data/sample_gasto.csv` — 50 filas con edge cases
- [x] Crear `.env.example` — template de variables de entorno
- [x] Actualizar `requirements.txt` — +pytest, +joblib
- [x] Actualizar `.gitignore` — excepción tests/data/*.csv, +logs/

## Fase 0 — Setup del entorno [COMPLETADA]

- [x] Instalar JDK 17 (Temurin)
- [x] Crear venv con PySpark 4.1.2
- [x] Configurar winutils.exe + hadoop.dll + HADOOP_HOME
- [x] Crear `src/verificar_spark.py`
- [x] Verificar: SparkSession, 32 cores, escritura Parquet OK
- [x] Commit y documentar en plan_v2.md

## Fase 1 — Conceptos fundamentales de Spark [COMPLETADA]

- [x] Refactorizar `src/verificar_spark.py` para usar config/
- [x] Crear `src/spark_conceptos.py`
- [x] Demostrar SparkSession: creación, configuración, singleton
- [x] Demostrar lazy evaluation: transformaciones vs acciones con tiempos
- [x] Demostrar plan de ejecución (explain(True))
- [x] Demostrar particiones: repartition(), coalesce()
- [x] Demostrar cache: cache(), unpersist(), comparación de tiempos
- [x] Demostrar agregaciones: DataFrame API vs Spark SQL
- [ ] Ejecutar script y documentar resultados
- [ ] Commit descriptivo

## Fase 2 — Ingesta del dataset completo [COMPLETADA]

- [x] Crear `src/ingesta/descarga.py` — HTTP streaming + reintentos con backoff
- [x] Crear `src/ingesta/lector_csv.py` — schema explícito (49 columnas MEF)
- [ ] Ejecutar ingesta del CSV completo con métricas loggeadas
- [ ] Benchmark: schema explícito vs inferSchema=True
- [ ] Documentar conteo total de registros
- [ ] Commit descriptivo

## Fase 3 — Filtro calidad UAT en Spark [COMPLETADA]

- [x] Crear `src/calidad/filtros_uat.py` — reglas UAT (monto > 0, distrito no vacío)
- [x] Crear `src/calidad/metricas.py` — tracking JSON con historial
- [x] Crear `tests/test_calidad.py` — 9 tests pytest
- [ ] Ejecutar `python -m pytest tests/test_calidad.py -v`
- [ ] Comparar resultados con v1 (deben coincidir)
- [ ] Commit descriptivo

## Fase 4 — Agregaciones y Parquet particionado [COMPLETADA]

- [x] Crear `src/agregacion/transformaciones.py` — groupBy por depto y sector
- [x] Crear `src/agregacion/escritor_parquet.py` — writer particionado
- [x] Crear `tests/test_agregacion.py` — 12 tests pytest
- [x] Agregaciones con DataFrame API
- [x] Agregaciones equivalentes con Spark SQL
- [ ] Ejecutar `python -m pytest tests/test_agregacion.py -v`
- [ ] Ejecutar pipeline completo + Parquet escrito
- [ ] Benchmark v1 (SQLite) vs v2 (Spark)
- [ ] Commit descriptivo

## Fase 5 — EDA (Análisis Exploratorio) [PENDIENTE]

- [ ] Crear rama `feature/eda`
- [ ] Crear carpeta `notebooks/`
- [ ] Crear `notebooks/01_eda.ipynb`
- [ ] Estadísticas descriptivas (media, mediana, std, percentiles)
- [ ] Distribución de MONTO_DEVENGADO por departamento y sector
- [ ] Análisis de correlación (heatmap)
- [ ] Detección de outliers (IQR, Z-score)
- [ ] Visualizaciones: histogramas, boxplots, scatter plots
- [ ] Conclusiones para feature engineering (justificar features para ML)
- [ ] Commit descriptivo

## Fase 6 — Machine Learning con scikit-learn [PENDIENTE]

- [ ] Crear rama `feature/ml-sklearn`
- [ ] Crear `notebooks/02_ml_sklearn.ipynb`
- [ ] Preparación de datos: encoding, scaling, train/test split
- [ ] Modelo 1 — Regresión (predecir MONTO_DEVENGADO)
  - [ ] Linear Regression
  - [ ] Random Forest Regressor
  - [ ] Gradient Boosting Regressor
  - [ ] Métricas: RMSE, MAE, R²
  - [ ] Cross-validation (k=5)
- [ ] Modelo 2 — Clustering (agrupar jurisdicciones)
  - [ ] K-Means + Elbow Method
  - [ ] DBSCAN
  - [ ] Silhouette Score
  - [ ] Interpretación de clusters
- [ ] Feature importance y explicabilidad
- [ ] Serializar mejores modelos en `models/`
- [ ] Commit descriptivo

## Fase 7 — ML distribuido con PySpark MLlib [PENDIENTE]

- [ ] Crear rama `feature/ml-spark`
- [ ] Crear `src/spark_ml_pipeline.py`
- [ ] Pipeline: VectorAssembler → StringIndexer → modelo → evaluación
- [ ] Modelos: LinearRegression, RandomForestRegressor, GBTRegressor
- [ ] Comparativa: scikit-learn vs MLlib (métricas y tiempos)
- [ ] Commit descriptivo

## Fase 8 — Databricks Community Edition [PENDIENTE]

- [ ] Crear rama `feature/databricks`
- [ ] Crear cuenta en Databricks Community Edition
- [ ] Subir datos y crear notebooks
- [ ] Replicar pipeline: ingesta → calidad → agregación
- [ ] Replicar pipeline ML con MLflow tracking
- [ ] Usar Delta Lake para persistencia
- [ ] Capturar evidencia (screenshots / notebooks exportados)
- [ ] Documentar diferencias local vs Databricks
- [ ] Commit descriptivo

## Fase 9 — Dashboard avanzado [PENDIENTE]

- [ ] Crear rama `feature/dashboard-v2`
- [ ] Crear `app_dashboard_v2.py`
- [ ] Sección descriptiva: KPIs + distribución por depto/sector
- [ ] Sección predictiva: predicciones del modelo + intervalos
- [ ] Sección clustering: grupos de jurisdicciones
- [ ] Sección benchmark: comparativa v1 vs v2 visualizada
- [ ] Filtros interactivos (departamento, sector, rango)
- [ ] Commit descriptivo

## Fase 10 — Documentación final y merge [PENDIENTE]

- [ ] Crear README.md v2 con arquitectura, capturas, resultados
- [ ] Tabla comparativa v1 vs v2 con métricas reales
- [ ] Registro completo de decisiones de arquitectura
- [ ] Merge de todas las ramas a main
- [ ] Tag de release v2.0
