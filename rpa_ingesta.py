import sqlite3
import requests
import io
import csv

# Configuración del proyecto
DB_NAME = "revenue_operations.db"
# Usamos un enlace real de Datos Abiertos del MEF
MEF_DATA_URL = "https://fs.datosabiertos.mef.gob.pe/datastorefiles/2020-Gasto.csv"

def inicializar_base_datos():
    """Crea la estructura relacional oficial en SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla principal para almacenar el gasto público auditado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gasto_mef (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano_eje TEXT,
            mes_eje TEXT,
            tipo_gobierno TEXT,
            sector TEXT,
            monto_ejecutado REAL,
            estado_auditoria TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("[BACKEND] Base de datos relacional inicializada correctamente.")

def descargar_y_procesar_mef():
    """Descarga el dataset, limpia anomalías y guarda las métricas presupuestales del MEF."""
    print(f"🚀 Conectando con los servidores del MEF vía HTTP GET...")
    headers = {"User-Agent": "Mozilla/5.0"}
    archivo_temporal = "gasto_2020_temp.csv"
    
    try:
        response = requests.get(MEF_DATA_URL, headers=headers, stream=True, timeout=15)
        
        if response.status_code == 200:
            print("📥 Descargando fragmento de producción en disco...")
            with open(archivo_temporal, "wb") as f:
                for chunk in response.iter_content(chunk_size=102400):
                    if chunk:
                        f.write(chunk)
                        if f.tell() > 8000000: # Descargamos 8 MB para asegurar capturar datos con montos > 0
                            break
            
            # Re-inicializamos la tabla con la estructura correcta para el MEF
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS gasto_mef")
            cursor.execute("""
                CREATE TABLE gasto_mef (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ano_eje TEXT,
                    mes_eje TEXT,
                    tipo_gobierno TEXT,
                    sector TEXT,
                    distrito TEXT,
                    monto_ejecutado REAL
                )
            """)
            
            print("✅ Estructura MEF creada. Aplicando reglas UAT en base a MONTO_DEVENGADO...")
            
            with open(archivo_temporal, "r", encoding="utf-8", errors="ignore") as f:
                csv_reader = csv.DictReader(f)
                
                validos = 0
                corruptos = 0
                
                for i, fila in enumerate(csv_reader):
                    if validos >= 150: # Guardamos 150 registros reales para alimentar el gráfico
                        break
                        
                    # Extracción selectiva de las columnas estratégicas
                    ano = fila.get("ANO_EJE", "2020")
                    mes = fila.get("MES_EJE", "N/A")
                    gobierno = fila.get("NIVEL_GOBIERNO_NOMBRE", "N/A")
                    sector_nombre = fila.get("SECTOR_NOMBRE", "N/A")
                    distrito_nombre = fila.get("DISTRITO_EJECUTORA_NOMBRE", "N/A")
                    
                    # Target Métrica: MONTO_DEVENGADO (Gasto Real)
                    monto_raw = fila.get("MONTO_DEVENGADO", "0")
                    
                    try:
                        monto = float(monto_raw) if monto_raw else 0.0
                        
                        # REGLA UAT: Filtrar correcciones negativas o registros sin ejecutar (0.0)
                        if monto <= 0:
                            corruptos += 1
                            continue
                        
                        cursor.execute("""
                            INSERT INTO gasto_mef (ano_eje, mes_eje, tipo_gobierno, sector, distrito, monto_ejecutado)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (ano, mes, gobierno, sector_nombre, distrito_nombre, monto))
                        
                        print(f"🔹 [UAT] Registro {validos + 1} insertado: {sector_nombre} en {distrito_nombre} -> S/. {monto}")
                        validos += 1
                        
                    except:
                        corruptos += 1
                        continue
                        
            conn.commit()
            conn.close()
            
            print("\n========================================")
            print("📊 PIPELINE CONCLUIDO CON ÉXITO")
            print(f"   Registros reales guardados en SQLite: {validos}")
            print(f"   Registros descartados (Ceros/Negativos): {corruptos}")
            print("========================================")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inicializar_base_datos()
    descargar_y_procesar_mef()