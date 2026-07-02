import sqlite3
import random
from datetime import datetime, timedelta

# Configuración del entorno local seguro
DB_NAME = "revenue_operations.db"

def conectar_db():
    """Establece la conexión con la base de datos relacional SQLite."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def inicializar_tablas():
    """Crea la estructura relacional para el análisis de negocio (SaaS)."""
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Tabla de transacciones comerciales (Métricas SaaS: MRR, Churn)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contratos_crm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT NOT NULL,
            monto_mrr REAL,
            estado TEXT,
            fecha_registro TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f" [UAT] Base de datos '{DB_NAME}' e infraestructura relacional inicializadas.")

def simular_ingesta_crm():
    """Simula la extracción masiva de datos desde una API de CRM (HubSpot/Salesforce)."""
    estados_validos = ["ACTIVO", "RENOVADO", "CHURN", "PENDIENTE", None] # Incluye nulos para probar UAT
    datos_extraidos = []
    
    base_fecha = datetime.now()
    for i in range(1, 101): # Generamos 100 registros de prueba
        cliente_id = f"CLI-{1000 + i}"
        monto = round(random.uniform(-50.0, 500.0), 2) # Montos negativos simulados para romper UAT
        estado = random.choice(estados_validos)
        fecha = (base_fecha - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        
        datos_extraidos.append((cliente_id, monto, estado, fecha))
    
    return datos_extraidos

def pipeline_etl_con_uat():
    """Ejecuta el proceso ETL aplicando reglas estrictas de Calidad de Datos (UAT)."""
    print("🚀 Iniciando Pipeline de Ingesta Automatizada...")
    inicializar_tablas()
    
    raw_data = simular_ingesta_crm()
    conn = conectar_db()
    cursor = conn.cursor()
    
    registros_validos = 0
    registros_corruptos = 0
    
    for registro in raw_data:
        cliente_id, monto, estado, fecha = registro
        
        # --- REGLAS DE CONTROL DE CALIDAD (UAT) ---
        if monto is None or monto <= 0:
            print(f" ⚠️ [LOG UAT - ERROR]: Cliente {cliente_id} rechazado. Monto inválido: {monto}")
            registros_corruptos += 1
            continue
            
        if estado is None or estado not in ["ACTIVO", "RENOVADO", "CHURN", "PENDIENTE"]:
            print(f" ⚠️ [LOG UAT - ERROR]: Cliente {cliente_id} rechazado. Estado corrupto: {estado}")
            registros_corruptos += 1
            continue
        
        # Si pasa los filtros de calidad, se inserta en el almacén de datos
        cursor.execute('''
            INSERT INTO contratos_crm (cliente_id, monto_mrr, estado, fecha_registro)
            VALUES (?, ?, ?, ?)
        ''', (cliente_id, monto, estado, fecha))
        registros_validos += 1
        
    conn.commit()
    conn.close()
    
    print("\n" + "="*40)
    print("📊 RESUMEN DE CONTROL DE CALIDAD (ETL METRICS)")
    print(f" Registros procesados e insertados con éxito: {registros_validos}")
    print(f" Registros corruptos detectados e ignorados: {registros_corruptos}")
    print("="*40)

if __name__ == "__main__":
    pipeline_etl_con_uat()