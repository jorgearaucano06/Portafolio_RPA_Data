import sqlite3
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Auditoría de Gasto Público MEF", page_icon="🏛️", layout="wide")

DB_NAME = "revenue_operations.db"

def cargar_resumen_distritos():
    """Ejecuta una consulta SQL agregada directamente en el motor SQLite."""
    conn = sqlite3.connect(DB_NAME)
    # Aquí aplicamos el GROUP BY y SUM en SQL, directo en el motor relacional
    query = """
        SELECT distrito, SUM(monto_ejecutado) as total_ejecutado 
        FROM gasto_mef 
        GROUP BY distrito 
        ORDER BY total_ejecutado DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("🏛️ Plataforma Avanzada de Control Presupuestal - MEF")
st.markdown("Análisis agregativo de la ejecución financiera real por distritos de la República del Perú.")
st.markdown("---")

try:
    # Cargamos la tabla agrupada
    df_distritos = cargar_resumen_distritos()
    
    # ─── SECCIÓN: FILTROS DINÁMICOS MULTI-SELECCIÓN ───
    st.markdown("### 🔍 Filtros Interactivos de Auditoría")
    distritos_disponibles = df_distritos["distrito"].unique().tolist()
    
    # Selector dinámico en la interfaz
    distritos_seleccionados = st.multiselect(
        "Selecciona uno o varios distritos para comparar la ejecución:",
        options=distritos_disponibles,
        default=distritos_disponibles[:5] # Por defecto muestra los 5 distritos con mayor gasto
    )
    
    # Filtrado reactivo sobre el DataFrame
    df_filtrado = df_distritos[df_distritos["distrito"].isin(distritos_seleccionados)]
    
    st.markdown("---")
    
    # ─── SECCIÓN 2: RENDERIZADO VISUAL PREMIUM ───
    col_graf, col_tabla = st.columns([3, 2])
    
    with col_graf:
        st.markdown("### 📊 Inversión Pública Real Recaudada (S/.)")
        if not df_filtrado.empty:
            st.bar_chart(data=df_filtrado, x="distrito", y="total_ejecutado", use_container_width=True)
        else:
            st.warning("⚠️ Selecciona al menos un distrito para visualizar la gráfica.")
            
    with col_tabla:
        st.markdown("### 📋 Resumen Agregado Consolidado")
        st.dataframe(
            df_filtrado.rename(columns={"distrito": "Distrito Ejecutor", "total_ejecutado": "Total Devengado (S/.)"}),
            use_container_width=True, 
            height=320
        )

except Exception as e:
    st.error("⚠️ Estructura no actualizada. Corre 'python rpa_ingesta.py' primero.")