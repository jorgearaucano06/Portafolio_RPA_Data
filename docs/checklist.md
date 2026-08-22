# Checklist de progreso — Portafolio RPA & Data

> Referencia rapida para retomar el trabajo si se corta la sesion.
> Marcar con `[x]` cada paso completado. Actualizar la linea "Ultimo avance".

**Ultimo avance**: Fases 0-7 y 9 completadas (codigo + 30 tests). Pendiente: Fase 8 (Databricks) y Fase 10 (merge).
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
- [x] Actualizar `requirements.txt` — +pytest, +joblib, +matplotlib, +seaborn, +scipy
- [x] Actualizar `.gitignore` — excepcion tests/data/*.csv, +logs/

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
- [x] Demostrar SparkSession: creacion, configuracion, singleton
- [x] Demostrar lazy evaluation: transformaciones vs acciones con tiempos
- [x] Demostrar plan de ejecucion (explain(True))
- [x] Demostrar particiones: repartition(), coalesce()
- [x] Demostrar cache: cache(), unpersist(), comparacion de tiempos
- [x] Demostrar agregaciones: DataFrame API vs Spark SQL
- [x] Commit descriptivo

## Fase 2 — Ingesta del dataset completo [COMPLETADA]

- [x] Crear `src/ingesta/descarga.py` — HTTP streaming + reintentos con backoff
- [x] Crear `src/ingesta/lector_csv.py` — schema explicito (49 columnas MEF)
- [ ] Ejecutar ingesta del CSV completo y medir tiempos
- [ ] Benchmark: schema explicito vs inferSchema=True
- [x] Commit descriptivo

## Fase 3 — Filtro calidad UAT en Spark [COMPLETADA]

- [x] Crear `src/calidad/filtros_uat.py` — reglas UAT (monto > 0, distrito no vacio)
- [x] Crear `src/calidad/metricas.py` — tracking JSON con historial
- [x] Crear `tests/test_calidad.py` — 9 tests pytest
- [x] Ejecutar tests: 9/9 pasando
- [x] Commit descriptivo

## Fase 4 — Agregaciones y Parquet particionado [COMPLETADA]

- [x] Crear `src/agregacion/transformaciones.py` — groupBy por depto y sector
- [x] Crear `src/agregacion/escritor_parquet.py` — writer particionado
- [x] Crear `tests/test_agregacion.py` — 11 tests pytest
- [x] Agregaciones con DataFrame API
- [x] Agregaciones equivalentes con Spark SQL
- [x] Ejecutar tests: 11/11 pasando
- [ ] Ejecutar pipeline completo con datos reales + Parquet escrito
- [ ] Benchmark v1 (SQLite) vs v2 (Spark)
- [x] Commit descriptivo

## Fase 5 — EDA (Analisis Exploratorio) [COMPLETADA]

- [x] Crear `notebooks/01_eda.ipynb` — 29 celdas (12 narrativa + 17 codigo)
- [x] Estadisticas descriptivas (media, mediana, std, percentiles, asimetria, curtosis)
- [x] Distribucion de MONTO_DEVENGADO: histograma, log-scale, boxplot
- [x] Gasto por departamento: top 15, curva Pareto de concentracion
- [x] Gasto por sector: barras comparativas
- [x] Gasto por mes: estacionalidad
- [x] Analisis de correlacion (heatmap)
- [x] Deteccion de outliers (IQR + Z-score con visualizacion)
- [x] Distribucion por nivel de gobierno (pie + boxplot)
- [x] Conclusiones para feature engineering (decisiones documentadas para Fase 6)
- [x] Commit descriptivo

## Fase 6 — Machine Learning con scikit-learn [COMPLETADA]

- [x] Crear `src/ml/features.py` — feature engineering (registro + clustering)
- [x] Crear `src/ml/sklearn_models.py` — 3 regresores + 2 clustering
- [x] Crear `src/ml/evaluacion.py` — tracking JSON + serializacion joblib
- [x] Crear `notebooks/02_ml_sklearn.ipynb` — notebook completo
- [x] Crear `tests/test_features.py` — 10 tests pytest
- [x] Regresion: LinearRegression, RandomForest, GradientBoosting
  - [x] Metricas: RMSE, MAE, R2
  - [x] Cross-validation (k=5)
  - [x] Feature importance
- [x] Clustering: KMeans (Elbow Method) + DBSCAN
  - [x] Silhouette Score
  - [x] Visualizacion 2D con PCA
- [x] Serializacion de modelos con joblib
- [x] Ejecutar tests: 10/10 pasando
- [x] Commit descriptivo

## Fase 7 — ML distribuido con PySpark MLlib [COMPLETADA]

- [x] Crear `src/ml/spark_models.py`
- [x] Pipeline: StringIndexer -> OneHotEncoder -> VectorAssembler -> modelo
- [x] Modelos: LinearRegression, RandomForestRegressor, GBTRegressor
- [x] Funcion comparar_sklearn_vs_mllib() para tabla comparativa
- [x] Commit descriptivo

## Fase 8 — Databricks Community Edition [PENDIENTE]

- [ ] Crear cuenta en Databricks Community Edition
- [ ] Subir notebooks y datos
- [ ] Replicar pipeline: ingesta -> calidad -> agregacion
- [ ] Replicar pipeline ML con MLflow tracking
- [ ] Usar Delta Lake para persistencia
- [ ] Capturar evidencia (screenshots / notebooks exportados)
- [ ] Documentar diferencias local vs Databricks

## Fase 9 — Dashboard avanzado [COMPLETADA]

- [x] Crear `app_dashboard_v2.py`
- [x] Seccion descriptiva: KPIs + distribucion por depto/sector
- [x] Seccion predictiva: carga modelo serializado + muestra metricas
- [x] Seccion clustering: metricas + grafico Silhouette por K
- [x] Seccion benchmark: tabla comparativa v1 vs v2
- [x] Filtros interactivos (departamento, sector)
- [x] Deteccion automatica de fuente de datos (Parquet > CSV > sample)
- [x] Commit descriptivo

## Fase 10 — Documentacion final y merge [EN CURSO]

- [x] Actualizar README.md con arquitectura v2
- [x] Actualizar checklist con progreso real
- [ ] Tabla comparativa v1 vs v2 con metricas reales (requiere ejecucion con datos completos)
- [ ] Merge de todas las ramas a main
- [ ] Tag de release v2.0
