import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import struct
import io
from datetime import datetime

st.set_page_config(page_title="UMM Analyzer - Carga y Análisis", layout="wide")

# Estilo personalizado
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stButton button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 UMM Analyzer - Carga y Análisis de Datos")
st.markdown("---")

# Función para extraer datos del archivo .umm
def extraer_datos_umm(contenido_binario):
    """Extrae datos reales de un archivo .umm"""
    datos = []
    
    # Leer como shorts (2 bytes)
    for i in range(0, min(len(contenido_binario), 50000), 2):
        try:
            val = struct.unpack('h', contenido_binario[i:i+2])[0]
            # Filtrar valores de relleno (21845 = 0x5555)
            if val != 21845 and val != 0 and -10000 < val < 10000:
                datos.append(val)
        except:
            pass
    
    return datos

# Función para analizar el archivo
def analizar_archivo(contenido_binario):
    """Analiza el archivo y devuelve estadísticas"""
    info = {
        'tamaño': len(contenido_binario),
        'tipo': 'Desconocido',
        'estructura': {},
        'datos_extraidos': []
    }
    
    # Verificar si es binario o texto
    try:
        contenido_binario[:100].decode('utf-8')
        info['tipo'] = 'Texto'
    except:
        info['tipo'] = 'Binario'
    
    # Extraer datos
    info['datos_extraidos'] = extraer_datos_umm(contenido_binario)
    
    # Análisis de estructura
    primeros_bytes = contenido_binario[:20].hex()
    info['estructura']['primeros_bytes'] = primeros_bytes
    
    # Contar patrones
    patron_55 = contenido_binario.count(b'\x55')
    info['estructura']['patron_55'] = patron_55
    
    return info

# Sidebar
with st.sidebar:
    st.header("📂 Carga de archivo")
    
    # Subir archivo
    archivo_subido = st.file_uploader(
        "Selecciona un archivo .umm",
        type=['umm', 'UMM', 'csv', 'txt'],
        help="Arrastra o selecciona un archivo .umm para analizar"
    )
    
    st.markdown("---")
    st.header("⚙️ Configuración")
    
    # Opciones de extracción
    limite_muestras = st.slider(
        "Límite de muestras a extraer:",
        min_value=100,
        max_value=50000,
        value=5000,
        step=100,
        help="Cantidad máxima de valores a extraer del archivo"
    )
    
    # Mostrar información del archivo
    if archivo_subido is not None:
        st.success(f"✅ Archivo: {archivo_subido.name}")
        st.info(f"📏 Tamaño: {archivo_subido.size:,} bytes")
        
        # Botón para procesar
        if st.button("🚀 Procesar Archivo", type="primary", use_container_width=True):
            st.session_state['procesar'] = True

# Procesamiento principal
if archivo_subido is not None and st.session_state.get('procesar', False):
    try:
        # Leer el archivo
        contenido = archivo_subido.read()
        
        # Analizar el archivo
        with st.spinner("🔍 Analizando archivo..."):
            info = analizar_archivo(contenido)
            datos = info['datos_extraidos']
        
        # Guardar en session state
        st.session_state['datos'] = datos
        st.session_state['archivo'] = archivo_subido.name
        st.session_state['info'] = info
        
        st.success(f"✅ Archivo procesado correctamente!")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")

# Mostrar resultados
if 'datos' in st.session_state and st.session_state['datos']:
    datos = st.session_state['datos']
    nombre_archivo = st.session_state.get('archivo', 'archivo')
    info = st.session_state.get('info', {})
    
    # ============= INFORMACIÓN DEL ARCHIVO =============
    st.subheader("📋 Información del Archivo")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 Archivo", nombre_archivo)
    with col2:
        st.metric("📊 Datos extraídos", f"{len(datos):,}")
    with col3:
        st.metric("📏 Tipo", info.get('tipo', 'Desconocido'))
    with col4:
        st.metric("📐 Bytes", f"{info.get('estructura', {}).get('primeros_bytes', 'N/A')[:8]}...")
    
    st.markdown("---")
    
    # ============= ESTADÍSTICAS =============
    if datos:
        st.subheader("📊 Estadísticas de los datos")
        
        df_datos = pd.DataFrame({
            'Índice': range(len(datos)),
            'Valor': datos
        })
        
        # Métricas principales
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Cantidad", f"{len(datos):,}")
        with col2:
            st.metric("Mínimo", f"{min(datos):.2f}")
        with col3:
            st.metric("Máximo", f"{max(datos):.2f}")
        with col4:
            st.metric("Promedio", f"{sum(datos)/len(datos):.2f}")
        with col5:
            st.metric("Mediana", f"{np.median(datos):.2f}")
        
        # ============= ORGANIZACIÓN EN PARÁMETROS =============
        st.subheader("📊 Organización en Parámetros")
        
        # Intentar organizar en bloques de 10
        num_parametros = 10
        num_filas = len(datos) // num_parametros
        
        if num_filas > 0:
            matriz = np.array(datos[:num_filas * num_parametros]).reshape(num_filas, num_parametros)
            
            nombres_param = ['Modo', 'Frecuencia', 'Corriente', 'Temperatura', 
                           'Velocidad', 'Torque', 'Voltaje', 'Potencia', 
                           'Factor_Potencia', 'Estado']
            
            df_parametros = pd.DataFrame(matriz, columns=nombres_param)
            
            st.success(f"✅ Datos organizados en {num_filas} registros de {num_parametros} parámetros")
            st.dataframe(df_parametros.head(10), use_container_width=True)
            
            # Mostrar valores actuales
            st.subheader("📊 Estado Actual")
            ultimo = df_parametros.iloc[-1]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Modo", f"{int(ultimo['Modo'])}")
                st.metric("Frecuencia", f"{ultimo['Frecuencia'] * 0.01:.2f} Hz")
            with col2:
                st.metric("Corriente", f"{ultimo['Corriente'] * 0.001:.3f} A")
                st.metric("Temperatura", f"{ultimo['Temperatura']:.0f} °C")
            with col3:
                st.metric("Velocidad", f"{ultimo['Velocidad'] * 0.01:.0f} RPM")
                st.metric("Torque", f"{ultimo['Torque'] * 0.01:.2f} Nm")
            with col4:
                st.metric("Voltaje", f"{ultimo['Voltaje'] * 0.01:.2f} V")
                st.metric("Potencia", f"{ultimo['Potencia'] * 0.001:.3f} kW")
            
            # Gráfico de parámetros
            st.subheader("📈 Evolución de parámetros")
            parametros_seleccionados = st.multiselect(
                "Selecciona parámetros para graficar:",
                nombres_param,
                default=['Frecuencia', 'Corriente', 'Temperatura']
            )
            
            if parametros_seleccionados:
                fig = px.line(df_parametros, y=parametros_seleccionados,
                             title="Evolución de parámetros del variador",
                             labels={'index': 'Muestra', 'value': 'Valor'})
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            # Guardar organizado
            st.session_state['df_parametros'] = df_parametros
            
        else:
            st.warning("⚠️ No se pudieron organizar los datos en parámetros")
        
        # ============= GRÁFICOS =============
        st.subheader("📈 Visualización de datos")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolución", "📊 Histograma", "📦 Boxplot", "🔗 Correlación"])
        
        with tab1:
            muestras = st.slider("Muestras a mostrar:", 100, min(5000, len(datos)), 1000)
            df_plot = pd.DataFrame({
                'Índice': range(muestras),
                'Valor': datos[:muestras]
            })
            
            fig = px.line(df_plot, x='Índice', y='Valor',
                         title=f"Evolución de datos (primeras {muestras} muestras)",
                         labels={'Índice': 'Muestra', 'Valor': 'Valor'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig_hist = px.histogram(df_datos, x='Valor', nbins=50,
                                   title="Distribución de valores")
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with tab3:
            fig_box = px.box(df_datos, y='Valor', title="Diagrama de caja")
            fig_box.update_layout(height=400)
            st.plotly_chart(fig_box, use_container_width=True)
        
        with tab4:
            if 'df_parametros' in st.session_state:
                df_corr = st.session_state['df_parametros']
                if len(df_corr.columns) > 1:
                    corr = df_corr.corr()
                    fig_corr = px.imshow(corr, text_auto=True, aspect="auto",
                                        title="Matriz de correlación entre parámetros")
                    st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("ℹ️ Organiza los datos en parámetros para ver correlaciones")
        
        # ============= DATOS COMPLETOS =============
        st.subheader("📋 Datos completos")
        
        if st.checkbox("Mostrar datos completos"):
            st.dataframe(df_datos, use_container_width=True)
        
        # ============= EXPORTAR =============
        st.subheader("📥 Exportar datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exportar datos crudos
            csv_raw = df_datos.to_csv(index=False)
            st.download_button(
                label="📥 Descargar datos crudos (CSV)",
                data=csv_raw,
                file_name=f"{nombre_archivo}_datos_crudos.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Exportar parámetros si existen
            if 'df_parametros' in st.session_state:
                csv_param = st.session_state['df_parametros'].to_csv(index=False)
                st.download_button(
                    label="📥 Descargar parámetros organizados (CSV)",
                    data=csv_param,
                    file_name=f"{nombre_archivo}_parametros.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # ============= ANÁLISIS AVANZADO =============
        with st.expander("🔍 Análisis Avanzado del Archivo"):
            st.subheader("Estructura del archivo")
            
            # Mostrar primeros bytes
            st.write("**Primeros 50 bytes (hex):**")
            st.code(contenido[:50].hex() if 'contenido' in dir() else "No disponible")
            
            # Estadísticas detalladas
            st.write("**Estadísticas detalladas:**")
            st.dataframe(df_datos.describe(), use_container_width=True)
            
            # Valores únicos
            st.write("**Valores más frecuentes:**")
            top_valores = pd.Series(datos).value_counts().head(10)
            st.dataframe(top_valores.to_frame('Frecuencia'), use_container_width=True)
    
    else:
        st.warning("⚠️ No se encontraron datos válidos en el archivo")

else:
    # Pantalla de inicio
    st.info("👈 **Sube un archivo en el panel lateral para comenzar**")
    
    st.markdown("""
    ### 📋 ¿Cómo funciona?
    
    1. **Sube tu archivo** `.umm` desde el panel lateral
    2. La app **extrae automáticamente** los datos
    3. **Organiza** los datos en parámetros
    4. **Visualiza** los datos en gráficos interactivos
    5. **Exporta** los datos a CSV
    
    ### 📊 Formatos soportados:
    - ✅ `.umm` (archivos binarios)
    - ✅ `.UMM` (mayúsculas)
    - ✅ `.csv` (archivos de texto)
    - ✅ `.txt` (archivos de texto)
    
    ### 🔍 Datos que extrae:
    - Valores numéricos (shorts de 2 bytes)
    - Filtra datos de relleno (0x5555)
    - Organiza en parámetros de variador
    """)
    
    # Ejemplo de datos
    if st.button("📊 Cargar datos de ejemplo"):
        import numpy as np
        np.random.seed(42)
        datos_ejemplo = np.random.randint(-1000, 1000, 200).tolist()
        
        # Guardar en session state
        st.session_state['datos'] = datos_ejemplo
        st.session_state['archivo'] = "ejemplo.umm"
        
        st.success("✅ Datos de ejemplo cargados")
        st.rerun()

# Footer
st.markdown("---")
st.caption(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("🔧 Desarrollado con Streamlit | UMM Analyzer v2.0")
