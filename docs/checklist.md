# Checklist de progreso — Portafolio RPA & Data

> Referencia rapida para retomar el trabajo si se corta la sesion.
> Marcar con `[x]` cada paso completado. Actualizar la linea "Ultimo avance".

**Ultimo avance**: Fases 0-7 y 9 completadas (codigo + 30 tests + 3 commits locales).
**Rama activa**: `feature/spark-setup` (no se ha hecho push a GitHub todavia)
**Plan completo**: `docs/plan_v2.md`

---

## Estado general

| Componente | Archivos | Tests | Estado |
|-----------|----------|-------|--------|
| Infraestructura (config/, excepciones, pipeline) | 11 archivos | — | Listo |
| Fase 0 — Setup Spark | 1 archivo | — | Listo |
| Fase 1 — Conceptos Spark | 2 archivos | — | Listo |
| Fase 2 — Ingesta HTTP + CSV | 2 archivos | — | Codigo listo, falta ejecutar con datos reales |
| Fase 3 — Calidad UAT | 2 archivos | 9 tests | Listo |
| Fase 4 — Agregaciones + Parquet | 2 archivos | 11 tests | Codigo listo, falta pipeline con datos reales |
| Fase 5 — EDA | 1 notebook (29 celdas) | — | Listo |
| Fase 6 — ML sklearn | 3 archivos + 1 notebook | 10 tests | Listo |
| Fase 7 — ML MLlib | 1 archivo | — | Listo |
| Fase 8 — Databricks | — | — | Pendiente (manual, ver guia abajo) |
| Fase 9 — Dashboard v2 | 1 archivo | — | Listo |
| Fase 10 — Docs + merge | README + checklist | — | En curso |

**Total**: 30 tests pasando, 2 notebooks, ~35 archivos nuevos.

---

## Commits locales pendientes de push

```
9661b5a docs: actualizar README y checklist con progreso real de Fases 0-9
1bef92f feat: EDA, ML (sklearn + MLlib), dashboard v2 — Fases 5-7, 9
376c7ce feat: arquitectura profesional v2 + pipeline completo Fases 1-4
```

Para subir a GitHub: `git push origin feature/spark-setup`

---

## Infraestructura v2 [COMPLETADA]

- [x] `config/settings.py` — dataclasses frozen con toda la config
- [x] `config/spark_config.py` — factory de SparkSession
- [x] `config/logging_config.py` — logging profesional (stdlib)
- [x] `src/__init__.py` y subpaquetes (ingesta/, calidad/, agregacion/, ml/)
- [x] `src/excepciones.py` — PipelineError, DescargaError, CalidadError
- [x] `src/pipeline.py` — StageResult + ejecutar_pipeline()
- [x] `tests/conftest.py` — fixtures SparkSession + df_sample + df_limpio
- [x] `tests/data/sample_gasto.csv` — 50 filas con edge cases
- [x] `.env.example` — template de variables de entorno
- [x] `requirements.txt` — pyspark, streamlit, pandas, requests, pytest, joblib, matplotlib, seaborn, scipy
- [x] `.gitignore` — excepcion tests/data/*.csv, +logs/

## Fase 0 — Setup del entorno [COMPLETADA]

- [x] JDK 17 (Temurin) instalado
- [x] venv con PySpark 4.1.2
- [x] winutils.exe + hadoop.dll + HADOOP_HOME
- [x] `src/verificar_spark.py` — verificacion completa (32 cores, Parquet OK)

## Fase 1 — Conceptos Spark [COMPLETADA]

- [x] `src/verificar_spark.py` refactorizado para usar config/
- [x] `src/spark_conceptos.py` — SparkSession, lazy eval, explain, particiones, cache, agregaciones

## Fase 2 — Ingesta [COMPLETADA]

- [x] `src/ingesta/descarga.py` — HTTP streaming + reintentos con backoff (2s, 4s, 8s)
- [x] `src/ingesta/lector_csv.py` — schema explicito (49 columnas MEF)
- [ ] *Pendiente*: ejecutar ingesta del CSV completo (~500 MB) y medir tiempos

## Fase 3 — Calidad UAT [COMPLETADA]

- [x] `src/calidad/filtros_uat.py` — monto > 0, distrito no vacio, columna diagnostico
- [x] `src/calidad/metricas.py` — tracking JSON con historial y timestamps
- [x] `tests/test_calidad.py` — 9/9 tests pasando

## Fase 4 — Agregaciones + Parquet [COMPLETADA]

- [x] `src/agregacion/transformaciones.py` — groupBy por depto y sector (API + SQL)
- [x] `src/agregacion/escritor_parquet.py` — writer particionado
- [x] `tests/test_agregacion.py` — 11/11 tests pasando
- [ ] *Pendiente*: ejecutar pipeline completo con datos reales + benchmark v1 vs v2

## Fase 5 — EDA [COMPLETADA]

- [x] `notebooks/01_eda.ipynb` — 29 celdas
- [x] Estadisticas, distribuciones, correlacion, outliers (IQR + Z-score), conclusiones ML

## Fase 6 — ML scikit-learn [COMPLETADA]

- [x] `src/ml/features.py` — features por registro (one-hot) + por grupo (clustering)
- [x] `src/ml/sklearn_models.py` — LinearRegression, RandomForest, GBT + KMeans, DBSCAN
- [x] `src/ml/evaluacion.py` — tracking JSON + serializacion joblib + tabla comparativa
- [x] `notebooks/02_ml_sklearn.ipynb` — 18 celdas
- [x] `tests/test_features.py` — 10/10 tests pasando

## Fase 7 — ML MLlib [COMPLETADA]

- [x] `src/ml/spark_models.py` — pipeline StringIndexer -> OHE -> VectorAssembler -> modelo
- [x] Funcion comparar_sklearn_vs_mllib()

## Fase 8 — Databricks Free Edition [PENDIENTE]

> **Nota**: Community Edition se retiro en enero 2026. Usar **Free Edition** (gratis, sin tarjeta).
> **MLflow NO esta disponible** en Free Edition. El tracking local con JSON que construimos
> en `src/ml/evaluacion.py` cubre esa necesidad para el portafolio.

### Pasos para completar esta fase:

1. [ ] Crear cuenta en https://www.databricks.com/learn/free-edition (correo o Google)
2. [ ] En el workspace: Workspace > Import > subir `notebooks/01_eda.ipynb` y `02_ml_sklearn.ipynb`
3. [ ] Subir CSV: Data > Add data > subir `sample_gasto.csv` (o el CSV completo)
4. [ ] Ajustar notebooks para Databricks:
   - Quitar `from config.spark_config import crear_spark_session` (Spark ya existe)
   - Cambiar rutas de archivos a `/FileStore/tables/tu_archivo.csv`
   - La variable `spark` ya viene creada, no hay que instanciarla
5. [ ] Ejecutar notebooks y verificar que los resultados son coherentes con local
6. [ ] Tomar capturas de pantalla como evidencia
7. [ ] Documentar diferencias local vs Databricks en el notebook o en un markdown

## Fase 9 — Dashboard v2 [COMPLETADA]

- [x] `app_dashboard_v2.py` — 4 tabs: descriptivo, predictivo, clustering, benchmark
- [x] Filtros interactivos (departamento, sector)
- [x] Deteccion automatica de fuente de datos (Parquet > CSV > sample)
- [x] Ejecucion: `streamlit run app_dashboard_v2.py`

## Fase 10 — Documentacion final y merge [EN CURSO]

- [x] README.md actualizado con arquitectura v2, stack, instrucciones
- [x] Checklist actualizado con progreso real
- [ ] Merge de `feature/spark-setup` a `main` (cuando estes listo)
- [ ] Tag de release v2.0: `git tag -a v2.0 -m "v2 completa"`
- [ ] Push a GitHub: `git push origin main --tags`

---

## Comandos utiles para retomar

```bash
# Ver estado del repo
git status
git log --oneline -5

# Correr todos los tests
.venv\Scripts\python -m pytest tests/ -v

# Correr solo un grupo de tests
.venv\Scripts\python -m pytest tests/test_calidad.py -v
.venv\Scripts\python -m pytest tests/test_features.py -v

# Ejecutar conceptos de Spark
.venv\Scripts\python -m src.spark_conceptos

# Dashboard v2
streamlit run app_dashboard_v2.py

# Push a GitHub (cuando estes listo)
git push origin feature/spark-setup
```
