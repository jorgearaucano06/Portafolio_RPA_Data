import sqlite3
import streamlit as st
import pandas as pd

# Configuración de interfaz premium
st.set_page_config(page_title="Auditoría de Gasto Público MEF", page_icon="🏛️", layout="wide")

DB_NAME = "revenue_operations.db"

def cargar_datos_mef():
    """Extrae los registros validados de la nueva estructura del MEF."""
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM gasto_mef"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("🏛️ Plataforma de Control Presupuestal y Auditoría - MEF")
st.markdown("Procesamiento automatizado de datos abiertos gubernamentales bajo reglas de calidad UAT.")
st.markdown("---")

try:
    df_mef = cargar_datos_mef()
    
    # ─── SECCIÓN 1: KPIs EJECUTIVOS ───
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_registros = len(df_mef)
        st.metric(label="📊 Registros Auditados", value=total_registros)
        
    with col2:
        monto_total = round(df_mef["monto_ejecutado"].sum(), 2)
        st.metric(label="💰 Total Devengado (Gasto Real)", value=f"S/. {monto_total:,}")
        
    with col3:
        gasto_promedio = round(df_mef["monto_ejecutado"].mean(), 2)
        st.metric(label="📈 Gasto Promedio por Partida", value=f"S/. {gasto_promedio:,}")
        
    st.markdown("---")
    
    # ─── SECCIÓN 2: ANÁLISIS DISTRIBUTIVO ───
    col_graf, col_tabla = st.columns([3, 2])
    
    with col_graf:
        st.markdown("### 📈 Ejecución Financiera por Sector")
        # Agrupamos el gasto acumulado por cada sector del Estado
        gasto_por_sector = df_mef.groupby("sector")["monto_ejecutado"].sum().reset_index()
        st.bar_chart(data=gasto_por_sector, x="sector", y="monto_ejecutado", use_container_width=True)
        
    with col_tabla:
        st.markdown("### 🔍 Registros Validados en SQLite")
        # Mostramos la tabla limpia para la auditoría visual del analista
        st.dataframe(df_mef[["tipo_gobierno", "sector", "distrito", "monto_ejecutado"]], use_container_width=True, height=300)

except Exception as e:
    st.error("⚠️ Error al conectar con la estructura de datos del MEF. Asegúrate de correr 'python rpa_ingesta.py' primero.")