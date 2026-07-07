# Plan de migración v1 → v2: SQLite → PySpark + Parquet

> Hoja de ruta viva del proyecto. Se actualiza al cerrar cada fase.
> Regla de oro: **ninguna métrica se documenta sin haber sido medida.**

## Problema

La v1 procesa una **muestra de 40 MB** (~4-8% del dataset anual del MEF, que pesa
500 MB–1 GB) con un bucle Python fila a fila en **1 solo core**. No escala al
archivo completo.

## Solución

Migrar el motor de procesamiento a **PySpark** (procesamiento paralelo por
particiones), persistir en **Parquet particionado** y mantener la ingesta por
streaming HTTP que ya funciona. Replicar al final en **Databricks Free Edition**.

## Arquitectura v2

```
MEF Datos Abiertos (CSV COMPLETO ~500MB-1GB)
      |
      v  requests, stream=True, chunks (SE MANTIENE de v1)
data/raw/gasto_2020.csv          (local, fuera de Git)
      |
      v  spark.read.csv(schema explicito)
+---------------------------------------------+
|            PySpark  local[*]                |
|  Filtro UAT: filter / withColumn            |
|  Agregaciones: groupBy/agg + Spark SQL      |
|  N particiones -> todos los cores           |
+---------------------------------------------+
      |
      v  write.partitionBy("ano","departamento").parquet()
data/processed/  (Parquet particionado)
      |
      v  lectura de agregados pre-calculados
Streamlit (tarjetas KPI + sidebar de filtros)

Fase final: mismo pipeline portado a Databricks Free Edition
```

## Estado de fases

| Fase | Contenido | Rama | Estado |
|---|---|---|---|
| 0 | Setup: JDK 17, venv, PySpark 4.1.2, winutils, verificación | `feature/spark-setup` | ✅ Completada |
| 1 | Conceptos: SparkSession, lazy evaluation, transformaciones vs acciones | `feature/spark-setup` | ⬜ Pendiente |
| 2 | Ingesta dataset completo + `spark.read.csv` con schema explícito | `feature/spark-ingesta` | ⬜ Pendiente |
| 3 | Filtro calidad UAT en Spark + métricas reales válidos/rechazados | `feature/spark-calidad` | ⬜ Pendiente |
| 4 | Agregaciones (DataFrame API + Spark SQL), Parquet particionado, benchmark v1 vs v2 | `feature/spark-agregacion` | ⬜ Pendiente |
| 5 | Dashboard Streamlit leyendo Parquet | `feature/dashboard-parquet` | ⬜ Pendiente |
| 6 | Réplica en Databricks Free Edition | `feature/databricks` | ⬜ Pendiente |
| 7 | README v2, comparativa medida, decisiones de arquitectura, merge a main | `main` | ⬜ Pendiente |

## Fase 0 — Resultados medidos

- PySpark **4.1.2** sobre JDK **Temurin 17.0.19** (Python 3.14.6, venv).
- Paralelismo local detectado: **32 cores** (`local[*]`).
- Escritura Parquet verificada (compresión snappy, marcador `_SUCCESS`).

## Decisiones de arquitectura (registro)

| # | Decisión | Alternativas | Por qué |
|---|---|---|---|
| 1 | JDK 17 (Temurin) | JDK 21, quedarse en Java 8 | Spark 4 exige 17+; 17 es el LTS más extendido en la industria. El Java 8 previo (2017) no puede ejecutar bytecode de Spark 4. |
| 2 | `winutils.exe` + `hadoop.dll` + `HADOOP_HOME` | WSL2, Docker, desarrollar solo en Databricks | Spark delega la E/S en librerías Hadoop diseñadas para Linux; en Windows requieren estos binarios nativos. Es la opción mínima para desarrollo local. En producción (Linux) este problema no existe. |
| 3 | Versiones fijadas en `requirements.txt` | Dependencias sin versión | Reproducibilidad: quien clone el repo obtiene el mismo entorno. |
| 4 | Schema explícito en `spark.read.csv` (Fase 2) | `inferSchema=True` | Se justificará y medirá en Fase 2. |
| 5 | Parquet particionado por año y departamento (Fase 4) | CSV, un solo archivo | Se justificará y medirá en Fase 4. |

## Reglas del proyecto

1. Ningún dato al repo (`.gitignore` bloquea `*.csv`, `*.db`, `*.parquet`, `data/`).
2. Una rama por fase, commits descriptivos.
3. Métricas: solo las medidas. Si no se midió, no se escribe.
4. Todo error de entorno se documenta con su causa raíz (material de entrevista).
