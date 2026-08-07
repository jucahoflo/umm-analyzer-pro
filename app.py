import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import struct
from pathlib import Path
import numpy as np

st.set_page_config(page_title="UMM Analyzer - Datos Reales", layout="wide")
st.title("📊 UMM Analyzer - Visualizador de Datos Reales")

def extraer_datos_reales(ruta_archivo, limite=None):
    """Extrae solo los valores que no son relleno (21845)"""
    datos = []
    with open(ruta_archivo, 'rb') as f:
        contenido = f.read()
        
        max_iter = len(contenido) if limite is None else limite * 2
        
        for i in range(0, min(len(contenido), max_iter), 2):
            try:
                val = struct.unpack('h', contenido[i:i+2])[0]
                if val != 21845 and val != 0 and -10000 < val < 10000:
                    datos.append(val)
            except:
                pass
    
    return datos

# Sidebar
st.sidebar.header("📂 Configuración")
carpeta = Path("umm")
archivos_umm = list(carpeta.glob("*.umm")) + list(carpeta.glob("*.UMM"))

if archivos_umm:
    nombres = [f.name for f in archivos_umm]
    archivo_sel = st.sidebar.selectbox("Selecciona un archivo:", nombres)
    
    if archivo_sel:
        ruta = carpeta / archivo_sel
        st.sidebar.info(f"📏 Tamaño: {ruta.stat().st_size:,} bytes")
        
        if st.sidebar.button("🚀 Extraer datos reales", type="primary"):
            with st.spinner("Extrayendo datos..."):
                datos = extraer_datos_reales(ruta)
            
            if datos:
                st.session_state['datos'] = datos
                st.session_state['archivo'] = archivo_sel
                st.success(f"✅ {len(datos):,} datos reales extraídos")
            else:
                st.error("❌ No se encontraron datos reales")
else:
    st.sidebar.warning("⚠️ No hay archivos .umm en la carpeta 'umm'")

# Mostrar datos si existen
if 'datos' in st.session_state and st.session_state['datos']:
    datos = st.session_state['datos']
    archivo = st.session_state.get('archivo', 'datos')
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Gráficos", "📊 Estadísticas", "📋 Datos", "📥 Exportar"])
    
    with tab1:
        st.subheader("📈 Visualización de datos")
        
        col1, col2 = st.columns(2)
        with col1:
            muestras = st.slider(
                "Muestras a graficar:",
                min_value=10,
                max_value=min(len(datos), 5000),
                value=min(len(datos), 500),
                step=10
            )
        with col2:
            tipo_grafico = st.selectbox(
                "Tipo de gráfico:",
                ["Línea", "Barras", "Dispersión", "Área"]
            )
        
        df_plot = pd.DataFrame({
            'Muestra': range(muestras),
            'Valor': datos[:muestras]
        })
        
        if tipo_grafico == "Línea":
            fig = px.line(df_plot, x='Muestra', y='Valor',
                         title=f"Datos reales de {archivo}",
                         labels={'Muestra': 'Índice', 'Valor': 'Valor'})
        elif tipo_grafico == "Barras":
            fig = px.bar(df_plot, x='Muestra', y='Valor',
                        title=f"Datos reales de {archivo}")
        elif tipo_grafico == "Dispersión":
            fig = px.scatter(df_plot, x='Muestra', y='Valor',
                           title=f"Datos reales de {archivo}")
        else:
            fig = px.area(df_plot, x='Muestra', y='Valor',
                         title=f"Datos reales de {archivo}")
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Histograma
        st.subheader("📊 Distribución de valores")
        fig_hist = px.histogram(df_plot, x='Valor', nbins=50,
                               title="Distribución de valores")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Boxplot
        fig_box = px.box(df_plot, y='Valor', title="Diagrama de caja")
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab2:
        st.subheader("📊 Estadísticas detalladas")
        
        df_stats = pd.DataFrame(datos, columns=['Valor'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Cantidad", f"{len(datos):,}")
        with col2:
            st.metric("📉 Mínimo", f"{min(datos):,}")
        with col3:
            st.metric("📈 Máximo", f"{max(datos):,}")
        with col4:
            st.metric("📊 Promedio", f"{sum(datos)/len(datos):.2f}")
        
        st.dataframe(df_stats.describe(), use_container_width=True)
        
        # Percentiles
        st.subheader("📊 Percentiles")
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        valores_percentiles = [np.percentile(datos, p) for p in percentiles]
        df_percentiles = pd.DataFrame({
            'Percentil': percentiles,
            'Valor': valores_percentiles
        })
        st.dataframe(df_percentiles, use_container_width=True)
        
        # Conteo de valores únicos
        st.subheader("🔢 Valores únicos")
        valores_unicos = pd.Series(datos).value_counts().head(20)
        st.dataframe(valores_unicos.to_frame('Frecuencia'), use_container_width=True)
    
    with tab3:
        st.subheader("📋 Datos completos")
        
        filas = st.slider("Filas a mostrar:", 10, min(500, len(datos)), 50)
        df_tabla = pd.DataFrame({
            'Índice': range(filas),
            'Valor': datos[:filas]
        })
        st.dataframe(df_tabla, use_container_width=True)
        
        # Búsqueda de valores
        st.subheader("🔍 Buscar valores")
        valor_buscar = st.number_input("Buscar valor:", value=0)
        if st.button("Buscar"):
            indices = [i for i, v in enumerate(datos) if v == valor_buscar]
            if indices:
                st.success(f"✅ Encontrado en índices: {indices[:20]}")
            else:
                st.warning("❌ Valor no encontrado")
    
    with tab4:
        st.subheader("📥 Exportar datos")
        
        df_export = pd.DataFrame({
            'Índice': range(len(datos)),
            'Valor': datos
        })
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"{archivo}_datos_reales.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.info(f"📊 {len(datos):,} valores listos para descargar")
        
        # Mostrar vista previa
        st.subheader("📄 Vista previa del CSV")
        st.text(csv[:1000])
else:
    st.info("👈 Selecciona un archivo y haz clic en 'Extraer datos reales'")
    
    with st.expander("ℹ️ Información"):
        st.markdown("""
        ### 📋 ¿Qué hace esta app?
        1. Lee archivos `.umm` en formato binario
        2. Extrae valores que no son datos de relleno
        3. Muestra gráficos, estadísticas y tablas
        4. Permite exportar los datos a CSV
        
        ### 🔍 Los datos reales son:
        - Valores que no son 0 ni 21845 (0x5555)
        - Números en el rango -10000 a 10000
        - Probablemente parámetros de configuración
        """)
