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
    """Descarga un bloque masivo de producción y consolida la data por distritos en SQLite."""
    print(f"🚀 Conectando con los servidores del MEF vía HTTP GET...")
    headers = {"User-Agent": "Mozilla/5.0"}
    archivo_temporal = "gasto_2020_temp.csv"
    
    try:
        response = requests.get(MEF_DATA_URL, headers=headers, stream=True, timeout=15)
        
        if response.status_code == 200:
            print("📥 Descargando bloque masivo (40 MB) para capturar diversidad de distritos...")
            with open(archivo_temporal, "wb") as f:
                for chunk in response.iter_content(chunk_size=512000): # Bloques de 500 KB
                    if chunk:
                        f.write(chunk)
                        if f.tell() > 40000000: # Descargamos 40 MB de registros reales
                            break
            
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
            
            print("✅ Estructura relacional lista. Procesando y limpiando registros...")
            
            with open(archivo_temporal, "r", encoding="utf-8", errors="ignore") as f:
                csv_reader = csv.DictReader(f)
                
                validos = 0
                corruptos = 0
                registros_a_insertar = []
                
                for fila in csv_reader:
                    distrito_nombre = fila.get("DISTRITO_EJECUTORA_NOMBRE", "N/A").strip()
                    monto_raw = fila.get("MONTO_DEVENGADO", "0")
                    
                    try:
                        monto = float(monto_raw) if monto_raw else 0.0
                        # REGLA UAT: Omitir registros basura, negativos o sin ejecución
                        if monto <= 0 or distrito_nombre == "N/A" or distrito_nombre == "":
                            corruptos += 1
                            continue
                        
                        registros_a_insertar.append((
                            fila.get("ANO_EJE", "2020"),
                            fila.get("MES_EJE", "N/A"),
                            fila.get("NIVEL_GOBIERNO_NOMBRE", "N/A"),
                            fila.get("SECTOR_NOMBRE", "N/A"),
                            distrito_nombre,
                            monto
                        ))
                        validos += 1
                        
                    except:
                        corruptos += 1
                        continue
                
                # Inserción masiva eficiente (Bulk Insert) para acelerar el procesamiento
                cursor.executemany("""
                    INSERT INTO gasto_mef (ano_eje, mes_eje, tipo_gobierno, sector, distrito, monto_ejecutado)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, registros_a_insertar)
                
            conn.commit()
            conn.close()
            
            print("\n========================================")
            print("📊 PIPELINE CON MASIVIDAD DE DATOS CONCLUIDO")
            print(f"   Registros limpios indexados en SQLite: {validos}")
            print(f"   Registros descartados por calidad: {corruptos}")
            print("========================================")
            
    except Exception as e:
        print(f"❌ Error en Backend: {e}")

if __name__ == "__main__":
    inicializar_base_datos()
    descargar_y_procesar_mef()