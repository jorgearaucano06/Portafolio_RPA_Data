import sqlite3
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Auditoría de Gasto Público MEF", page_icon="🏛️", layout="wide")

DB_NAME = "revenue_operations.db"

def formatear_moneda_gerencial(monto):
    """Transforma números crudos en formato financiero corporativo (S/. M o K)."""
    if monto >= 1_000_000:
        return f"S/. {monto / 1_000_000:.1f} M"
    elif monto >= 1_000:
        return f"S/. {monto / 1_000:.1f} K"
    else:
        return f"S/. {monto:.2f}"

def cargar_resumen_distritos():
    """Extrae la información agrupada por distritos desde SQLite."""
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT distrito, SUM(monto_ejecutado) as total_ejecutado 
        FROM gasto_mef 
        GROUP BY distrito 
        ORDER BY total_ejecutado DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

try:
    df_distritos = cargar_resumen_distritos()
    
    # ─── BARRA LATERAL (SIDEBAR) PARA FILTROS ───
    st.sidebar.title("🔍 Filtros de Auditoría")
    st.sidebar.markdown("Use esta sección para segmentar las regiones analizadas.")
    distritos_disponibles = df_distritos["distrito"].unique().tolist()
    
    distritos_seleccionados = st.sidebar.multiselect(
        "Seleccione Distritos:",
        options=distritos_disponibles,
        default=distritos_disponibles[:5] # Muestra el Top 5 por defecto
    )
    
    # Filtrado dinámico
    df_filtrado = df_distritos[df_distritos["distrito"].isin(distritos_seleccionados)]
    
    # ─── ENCABEZADO PRINCIPAL ───
    st.title("🏛️ Dashboard de Control Presupuestal Ejecutivo - MEF")
    st.markdown("Análisis financiero de la ejecución presupuestal real del Estado peruano.")
    st.markdown("---")
    
    # ─── SECCIÓN 1: RE-INTRODUCCIÓN DE TARJETAS DE KPI SUPERIORES ───
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # KPI 1: Total de distritos bajo análisis en este momento
        total_distritos_activos = len(df_filtrado)
        st.metric(label="📊 Jurisdicciones Evaluadas", value=total_distritos_activos)
        
    with col2:
        # KPI 2: Suma financiera formateada a nivel gerencial
        monto_total_crudo = df_filtrado["total_ejecutado"].sum() if not df_filtrado.empty else 0
        monto_total_formateado = formatear_moneda_gerencial(monto_total_crudo)
        st.metric(label="💰 Gasto Real Devengado", value=monto_total_formateado)
        
    with col3:
        # KPI 3: Promedio de inversión de los elementos seleccionados
        gasto_promedio_crudo = df_filtrado["total_ejecutado"].mean() if not df_filtrado.empty else 0
        gasto_promedio_formateado = formatear_moneda_gerencial(gasto_promedio_crudo)
        st.metric(label="📈 Promedio de Ejecución", value=gasto_promedio_formateado)
        
    st.markdown("---")
    
    # ─── SECCIÓN 2: COMPONENTES VISUALES EN PARALELO ───
    col_graf, col_tabla = st.columns([3, 2])
    
    with col_graf:
        st.markdown("### 📊 Distribución del Gasto Público por Distrito")
        if not df_filtrado.empty:
            st.bar_chart(data=df_filtrado, x="distrito", y="total_ejecutado", use_container_width=True)
        else:
            st.warning("⚠️ Por favor, seleccione distritos en la barra lateral izquierda.")
            
    with col_tabla:
        st.markdown("### 📋 Tabla de Auditoría Consolidada")
        # Mostramos la tabla formateando los números crudos de forma elegante para el analista
        df_tabla_visual = df_filtrado.copy()
        df_tabla_visual["total_ejecutado"] = df_tabla_visual["total_ejecutado"].apply(formatear_moneda_gerencial)
        
        st.dataframe(
            df_tabla_visual.rename(columns={"distrito": "Distrito Ejecutor", "total_ejecutado": "Inversión Ejecutada"}),
            use_container_width=True, 
            height=320
        )

except Exception as e:
    st.error("⚠️ Estructura relacional no actualizada. Corra 'python rpa_ingesta.py' primero.")