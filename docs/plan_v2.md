# Plan v2: Data Engineering + Machine Learning Pipeline

> Hoja de ruta viva del proyecto. Se actualiza al cerrar cada fase.
> Regla de oro: **ninguna métrica se documenta sin haber sido medida.**

## Contexto

Este proyecto demuestra un pipeline end-to-end de **Data Engineering, Business
Intelligence y Machine Learning** sobre datos reales de ejecución presupuestal
del MEF (Perú). Cubre las competencias clave de un perfil **Científico de Datos /
Analista de BI**: ingesta masiva, procesamiento distribuido, modelado predictivo,
visualización avanzada y despliegue en la nube.

## Problema

La v1 procesa una **muestra de 40 MB** (~4-8% del dataset anual del MEF, que pesa
500 MB–1 GB) con un bucle Python fila a fila en **1 solo core**. No escala al
archivo completo. No incluye análisis predictivo ni está portado a la nube.

## Solución

Tres pilares:

1. **Data Engineering**: Migrar a **PySpark** (procesamiento paralelo) con
   persistencia en **Parquet particionado**.
2. **Machine Learning**: Construir modelos predictivos y de clustering sobre los
   datos procesados usando **scikit-learn** y **PySpark MLlib**.
3. **Cloud & BI**: Portar el pipeline a **Databricks** y construir un dashboard
   avanzado con métricas predictivas.

## Arquitectura v2

```
MEF Datos Abiertos (CSV COMPLETO ~500MB-1GB)
      |
      v  requests, stream=True, chunks (SE MANTIENE de v1)
data/raw/gasto_2020.csv               (local, fuera de Git)
      |
      v  spark.read.csv(schema explícito)
+--------------------------------------------------+
|             PySpark  local[*]                    |
|  Filtro UAT: filter / withColumn                 |
|  Feature Engineering: columnas derivadas         |
|  Agregaciones: groupBy/agg + Spark SQL           |
|  N particiones -> todos los cores                |
+--------------------------------------------------+
      |
      v  write.partitionBy("ano","departamento").parquet()
data/processed/  (Parquet particionado)
      |
      +---> Análisis Exploratorio (EDA)
      |         pandas, matplotlib, seaborn
      |         distribuciones, correlaciones, outliers
      |
      +---> Machine Learning
      |         scikit-learn: regresión, clasificación, clustering
      |         PySpark MLlib: pipeline distribuido
      |         métricas: RMSE, MAE, R², Silhouette Score
      |         artefactos: modelos serializados en models/
      |
      +---> Dashboard Avanzado (Streamlit)
      |         KPIs descriptivos + predicciones
      |         visualizaciones interactivas
      |
      v
Databricks Community Edition
      réplica del pipeline completo (ingesta → ML → visualización)
```

## Competencias demostradas por fase

| Competencia | Fases que la cubren |
|---|---|
| Python para datos (pandas, ETL) | 1, 2, 3, 5, 6 |
| SQL avanzado (Spark SQL) | 4 |
| PySpark / procesamiento distribuido | 1, 2, 3, 4 |
| Análisis estadístico y EDA | 5 |
| Machine Learning (scikit-learn) | 6 |
| ML distribuido (PySpark MLlib) | 7 |
| Databricks | 8 |
| Visualización avanzada / dashboards | 9 |
| Documentación técnica y benchmarks | 10 |

## Estado de fases

| Fase | Contenido | Rama | Estado |
|---|---|---|---|
| 0 | Setup: JDK 17, venv, PySpark 4.1.2, winutils, verificación | `feature/spark-setup` | ✅ Completada |
| 1 | Conceptos: SparkSession, lazy evaluation, transformaciones vs acciones | `feature/spark-setup` | ⬜ Pendiente |
| 2 | Ingesta dataset completo + `spark.read.csv` con schema explícito | `feature/spark-ingesta` | ⬜ Pendiente |
| 3 | Filtro calidad UAT en Spark + métricas reales válidos/rechazados | `feature/spark-calidad` | ⬜ Pendiente |
| 4 | Agregaciones (DataFrame API + Spark SQL), Parquet particionado, benchmark v1 vs v2 | `feature/spark-agregacion` | ⬜ Pendiente |
| 5 | EDA: análisis exploratorio con pandas/matplotlib sobre datos procesados | `feature/eda` | ⬜ Pendiente |
| 6 | ML con scikit-learn: modelos predictivos y clustering sobre datos del MEF | `feature/ml-sklearn` | ⬜ Pendiente |
| 7 | ML distribuido con PySpark MLlib: pipeline de ML a escala | `feature/ml-spark` | ⬜ Pendiente |
| 8 | Réplica en Databricks Community Edition (ingesta → ML → visualización) | `feature/databricks` | ⬜ Pendiente |
| 9 | Dashboard avanzado: métricas descriptivas + predicciones + visualización interactiva | `feature/dashboard-v2` | ⬜ Pendiente |
| 10 | README v2, comparativa medida, decisiones de arquitectura, merge a main | `main` | ⬜ Pendiente |

---

## Detalle por fase

### Fase 0 — Setup del entorno ✅

**Objetivo**: Entorno PySpark funcional en local.

**Resultados medidos**:
- PySpark **4.1.2** sobre JDK **Temurin 17.0.19** (Python 3.14.6, venv).
- Paralelismo local detectado: **32 cores** (`local[*]`).
- Escritura Parquet verificada (compresión snappy, marcador `_SUCCESS`).

---

### Fase 1 — Conceptos fundamentales de Spark

**Objetivo**: Demostrar comprensión de SparkSession, lazy evaluation y el modelo
de ejecución (transformaciones vs acciones).

**Entregables**:
- Script `src/spark_conceptos.py` con ejemplos documentados.
- Cada concepto demostrado con código ejecutable y salida medida.

---

### Fase 2 — Ingesta del dataset completo

**Objetivo**: Leer el CSV completo (~500 MB–1 GB) con `spark.read.csv` usando
schema explícito. Medir el impacto vs `inferSchema=True`.

**Entregables**:
- Script `src/spark_ingesta.py`.
- Benchmark medido: tiempo de lectura con schema explícito vs inferido.
- Conteo total de registros del dataset completo.

---

### Fase 3 — Filtro de calidad UAT en Spark

**Objetivo**: Replicar las reglas de calidad UAT de v1 en Spark (filter/withColumn).
Medir registros válidos vs rechazados.

**Entregables**:
- Script `src/spark_calidad.py`.
- Métricas: total ingestados, válidos, rechazados, % rechazo.
- Comparativa con v1: mismos resultados, diferente motor.

---

### Fase 4 — Agregaciones y Parquet particionado

**Objetivo**: Agregaciones con DataFrame API y Spark SQL. Persistir en Parquet
particionado por año y departamento. Benchmark v1 vs v2.

**Entregables**:
- Script `src/spark_agregacion.py`.
- Parquet particionado en `data/processed/`.
- Benchmark medido: v1 (SQLite single-core) vs v2 (Spark multi-core).
- Queries equivalentes en DataFrame API y Spark SQL.

---

### Fase 5 — Análisis Exploratorio de Datos (EDA)

**Objetivo**: Realizar un análisis estadístico riguroso sobre los datos
procesados para entender distribuciones, correlaciones y anomalías antes
de construir modelos de ML.

**Entregables**:
- Notebook `notebooks/01_eda.ipynb` con análisis completo.
- Análisis incluye:
  - Estadísticas descriptivas (media, mediana, desviación estándar, percentiles).
  - Distribución de `MONTO_DEVENGADO` por departamento y sector.
  - Análisis de correlación entre variables numéricas.
  - Detección de outliers (IQR, Z-score).
  - Visualizaciones: histogramas, boxplots, heatmaps, scatter plots.
- Conclusiones que justifiquen las features para los modelos de ML.

**Herramientas**: pandas, matplotlib, seaborn, scipy.stats.

---

### Fase 6 — Machine Learning con scikit-learn

**Objetivo**: Construir modelos predictivos y de clustering sobre los datos de
ejecución presupuestal, demostrando el ciclo completo de ML.

**Entregables**:
- Notebook `notebooks/02_ml_sklearn.ipynb`.
- **Modelo 1 — Regresión**: Predecir el monto de ejecución presupuestal
  (`MONTO_DEVENGADO`) por jurisdicción/sector.
  - Features: departamento, sector, fuente de financiamiento, tipo de recurso.
  - Modelos a evaluar: Linear Regression, Random Forest, Gradient Boosting.
  - Métricas: RMSE, MAE, R².
  - Validación: cross-validation (k=5), train/test split 80/20.
- **Modelo 2 — Clustering**: Agrupar jurisdicciones por patrones de ejecución.
  - Algoritmos: K-Means, DBSCAN.
  - Métricas: Silhouette Score, Elbow Method.
  - Interpretación de clusters (¿qué caracteriza a cada grupo?).
- Feature importance y explicabilidad del modelo.
- Modelos serializados en `models/` (joblib/pickle).

**Herramientas**: scikit-learn, pandas, matplotlib, seaborn.

---

### Fase 7 — ML distribuido con PySpark MLlib

**Objetivo**: Replicar el pipeline de ML en PySpark MLlib para demostrar
capacidad de procesamiento a escala con ML distribuido.

**Entregables**:
- Script `src/spark_ml_pipeline.py`.
- Pipeline MLlib: VectorAssembler → StringIndexer → modelo → evaluación.
- Modelos: LinearRegression, RandomForestRegressor, GBTRegressor.
- Comparativa medida: scikit-learn (single-node) vs MLlib (distribuido).
- Métricas equivalentes para validar consistencia entre ambos enfoques.

**Herramientas**: pyspark.ml, pyspark.ml.feature, pyspark.ml.evaluation.

---

### Fase 8 — Réplica en Databricks Community Edition

**Objetivo**: Portar el pipeline completo (ingesta → procesamiento → ML →
visualización) a Databricks, demostrando capacidad de trabajo en la nube.

**Entregables**:
- Notebooks en Databricks con el pipeline replicado.
- Uso de Delta Lake para persistencia (mejora sobre Parquet raw).
- MLflow para tracking de experimentos y registro de modelos.
- Capturas de pantalla / exportación de notebooks como evidencia.
- Documentación de diferencias: local vs Databricks (configuración, rendimiento).

**Herramientas**: Databricks Community Edition, Delta Lake, MLflow, Spark SQL.

---

### Fase 9 — Dashboard avanzado

**Objetivo**: Dashboard ejecutivo que integre métricas descriptivas y
predicciones del modelo de ML, con visualización interactiva.

**Entregables**:
- `app_dashboard_v2.py` (Streamlit).
- Secciones del dashboard:
  - **Descriptivo**: KPIs actuales, distribución por departamento/sector.
  - **Predictivo**: predicciones del modelo, intervalos de confianza.
  - **Clustering**: mapa de grupos de jurisdicciones con interpretación.
  - **Comparativa v1 vs v2**: benchmarks de rendimiento visualizados.
- Filtros interactivos: departamento, sector, rango de montos.
- Carga de datos desde Parquet pre-procesado.

---

### Fase 10 — Documentación final y merge

**Objetivo**: README v2 completo, comparativas medidas, consolidación.

**Entregables**:
- README.md actualizado con arquitectura v2, capturas, y resultados.
- Tabla comparativa v1 vs v2 con métricas reales.
- Registro completo de decisiones de arquitectura.
- Merge de todas las ramas a `main`.
- Tag de release `v2.0`.

---

## Decisiones de arquitectura (registro)

| # | Decisión | Alternativas | Por qué |
|---|---|---|---|
| 1 | JDK 17 (Temurin) | JDK 21, quedarse en Java 8 | Spark 4 exige 17+; 17 es el LTS más extendido en la industria. El Java 8 previo (2017) no puede ejecutar bytecode de Spark 4. |
| 2 | `winutils.exe` + `hadoop.dll` + `HADOOP_HOME` | WSL2, Docker, desarrollar solo en Databricks | Spark delega la E/S en librerías Hadoop diseñadas para Linux; en Windows requieren estos binarios nativos. Es la opción mínima para desarrollo local. En producción (Linux) este problema no existe. |
| 3 | Versiones fijadas en `requirements.txt` | Dependencias sin versión | Reproducibilidad: quien clone el repo obtiene el mismo entorno. |
| 4 | Schema explícito en `spark.read.csv` (Fase 2) | `inferSchema=True` | Se justificará y medirá en Fase 2. |
| 5 | Parquet particionado por año y departamento (Fase 4) | CSV, un solo archivo | Se justificará y medirá en Fase 4. |
| 6 | scikit-learn antes de MLlib (Fases 6→7) | Solo MLlib, solo scikit-learn | Primero scikit-learn para prototipado rápido y comprensión del modelo; luego MLlib para demostrar escalabilidad distribuida. Esto refleja el flujo real en la industria. |
| 7 | EDA como fase separada (Fase 5) | EDA integrado en la fase de ML | Separar el análisis exploratorio permite tomar decisiones informadas sobre feature engineering y selección de modelos antes de entrenar. |
| 8 | Databricks Community + MLflow (Fase 8) | Solo local, AWS/GCP | Databricks Community Edition es gratuito, incluye MLflow integrado y es la plataforma más demandada en el mercado para roles de Data Science. |

## Reglas del proyecto

1. Ningún dato al repo (`.gitignore` bloquea `*.csv`, `*.db`, `*.parquet`, `data/`).
2. Ningún modelo serializado al repo (`.gitignore` bloquea `models/`).
3. Una rama por fase, commits descriptivos.
4. Métricas: solo las medidas. Si no se midió, no se escribe.
5. Todo error de entorno se documenta con su causa raíz (material de entrevista).
6. Notebooks incluyen narrativa explicativa, no solo código.
