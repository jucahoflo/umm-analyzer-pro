import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import struct
import hashlib
from collections import Counter
from datetime import datetime
import io
import base64

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="UMM Analyzer Pro - Variador de Frecuencia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTILOS ====================
st.markdown("""
    <style>
        .main-header { text-align: center; padding: 1rem 0; }
        .metric-card { 
            background: #f0f2f6; 
            padding: 1rem; 
            border-radius: 10px; 
            text-align: center;
        }
        .success-box { 
            background: #d4edda; 
            padding: 1rem; 
            border-radius: 10px; 
            border-left: 5px solid #28a745;
        }
        .warning-box { 
            background: #fff3cd; 
            padding: 1rem; 
            border-radius: 10px; 
            border-left: 5px solid #ffc107;
        }
        .info-box { 
            background: #d1ecf1; 
            padding: 1rem; 
            border-radius: 10px; 
            border-left: 5px solid #17a2b8;
        }
        .stButton button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# ==================== CONSTANTES ====================
PARAMETROS = {
    'Modo': {'factor': 1, 'unidad': '', 'decimales': 0, 'rango': (0, 10)},
    'Frecuencia': {'factor': 0.01, 'unidad': 'Hz', 'decimales': 2, 'rango': (0, 5000)},
    'Corriente': {'factor': 0.001, 'unidad': 'A', 'decimales': 3, 'rango': (0, 10000)},
    'Temperatura': {'factor': 1, 'unidad': '°C', 'decimales': 0, 'rango': (-50, 150)},
    'Velocidad': {'factor': 0.01, 'unidad': 'RPM', 'decimales': 0, 'rango': (0, 6000)},
    'Torque': {'factor': 0.01, 'unidad': 'Nm', 'decimales': 2, 'rango': (-10000, 10000)},
    'Voltaje': {'factor': 0.01, 'unidad': 'V', 'decimales': 2, 'rango': (0, 10000)},
    'Potencia': {'factor': 0.001, 'unidad': 'kW', 'decimales': 3, 'rango': (0, 10000)},
    'Factor_Potencia': {'factor': 0.001, 'unidad': '', 'decimales': 3, 'rango': (0, 1000)},
    'Estado': {'factor': 1, 'unidad': '', 'decimales': 0, 'rango': (0, 20)}
}

NOMBRES_PARAM = ['Modo', 'Frecuencia', 'Corriente', 'Temperatura', 
                 'Velocidad', 'Torque', 'Voltaje', 'Potencia', 
                 'Factor_Potencia', 'Estado']

VALORES_RELLENO = [21845, -463, 0]

# ==================== FUNCIONES ====================

def extraer_datos_binarios(contenido, limite=50000):
    """Extrae datos del archivo binario .umm"""
    datos = []
    posiciones = []
    
    for i in range(0, min(len(contenido), limite), 2):
        try:
            val = struct.unpack('h', contenido[i:i+2])[0]
            if val not in VALORES_RELLENO and -10000 < val < 10000:
                datos.append(val)
                posiciones.append(i)
        except:
            pass
    
    return datos, posiciones

def organizar_parametros(datos):
    """Organiza los datos en bloques de 10 parámetros"""
    num_parametros = 10
    num_filas = len(datos) // num_parametros
    
    if num_filas == 0:
        return None, 0
    
    datos_limpios = datos[:num_filas * num_parametros]
    matriz = np.array(datos_limpios).reshape(num_filas, num_parametros)
    
    df = pd.DataFrame(matriz, columns=NOMBRES_PARAM)
    return df, num_filas

def aplicar_escalado(df):
    """Aplica factores de escalado a los parámetros"""
    df_escalado = df.copy()
    
    for col in df.columns:
        if col in PARAMETROS:
            factor = PARAMETROS[col]['factor']
            df_escalado[col] = df[col] * factor
    
    return df_escalado

def validar_datos(df):
    """Valida la calidad de los datos extraídos"""
    resultados = {
        'valido': False,
        'mensajes': [],
        'recomendaciones': [],
        'confianza': 0
    }
    
    if df is None or df.empty:
        resultados['mensajes'].append("❌ No hay datos para validar")
        return resultados
    
    fuera_rango = 0
    total_celdas = df.shape[0] * df.shape[1]
    
    for col in df.columns:
        if col in PARAMETROS:
            min_val, max_val = PARAMETROS[col]['rango']
            factor = PARAMETROS[col]['factor']
            if factor != 0:
                fuera = ((df[col] / factor) < min_val) | ((df[col] / factor) > max_val)
                fuera_rango += fuera.sum()
    
    porcentaje_fuera = (fuera_rango / total_celdas) * 100 if total_celdas > 0 else 0
    
    if porcentaje_fuera < 10:
        resultados['mensajes'].append(f"✅ {porcentaje_fuera:.1f}% de valores fuera de rango")
    else:
        resultados['mensajes'].append(f"⚠️ {porcentaje_fuera:.1f}% de valores fuera de rango")
        resultados['recomendaciones'].append("Verificar factores de escalado")
    
    valores_unicos = len(df.stack().unique())
    total_valores = df.size
    
    if valores_unicos / total_valores > 0.1:
        resultados['mensajes'].append(f"✅ Datos diversos ({valores_unicos} valores únicos)")
        resultados['confianza'] += 30
    else:
        resultados['mensajes'].append(f"⚠️ Baja diversidad de datos")
        resultados['recomendaciones'].append("Posiblemente datos de configuración")
    
    valores_sospechosos = 0
    for val in VALORES_RELLENO:
        count = (df == val).sum().sum()
        valores_sospechosos += count
    
    if valores_sospechosos == 0:
        resultados['mensajes'].append("✅ Sin valores de relleno detectados")
        resultados['confianza'] += 30
    elif valores_sospechosos < total_valores * 0.05:
        resultados['mensajes'].append(f"⚠️ {valores_sospechosos} valores sospechosos")
        resultados['confianza'] += 15
    else:
        resultados['mensajes'].append(f"❌ Demasiados valores sospechosos ({valores_sospechosos})")
        resultados['recomendaciones'].append("Verificar offset de extracción")
    
    if df.shape[0] > 100:
        resultados['mensajes'].append(f"✅ Suficientes datos ({df.shape[0]} registros)")
        resultados['confianza'] += 20
    elif df.shape[0] > 10:
        resultados['mensajes'].append(f"⚠️ Pocos datos ({df.shape[0]} registros)")
        resultados['confianza'] += 10
    else:
        resultados['mensajes'].append(f"❌ Datos insuficientes ({df.shape[0]} registros)")
        resultados['recomendaciones'].append("El archivo podría estar corrupto")
    
    resultados['valido'] = resultados['confianza'] >= 60
    
    if resultados['valido']:
        resultados['mensajes'].append("✅ DATOS VALIDADOS CON NIVEL DE CONFIANZA ALTO")
    else:
        resultados['mensajes'].append("⚠️ DATOS CON ADVERTENCIAS - REVISAR")
    
    return resultados

def calcular_estadisticas(df):
    """Calcula estadísticas detalladas del DataFrame"""
    estadisticas = {}
    
    for col in df.columns:
        if col in PARAMETROS:
            datos = df[col]
            estadisticas[col] = {
                'min': datos.min(),
                'max': datos.max(),
                'mean': datos.mean(),
                'std': datos.std(),
                'median': datos.median(),
                'q25': datos.quantile(0.25),
                'q75': datos.quantile(0.75),
            }
    
    return pd.DataFrame(estadisticas).T

def generar_reporte_html(df, nombre_archivo):
    """Genera un reporte HTML con los datos"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reporte UMM Analyzer</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            .table {{ border-collapse: collapse; width: 100%; }}
            .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .table th {{ background-color: #4CAF50; color: white; }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>📊 Reporte UMM Analyzer</h1>
        <p><strong>Archivo:</strong> {nombre_archivo}</p>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Registros:</strong> {len(df)}</p>
        
        <h2>📊 Estadísticas</h2>
        {df.describe().to_html()}
        
        <h2>📋 Datos</h2>
        {df.head(20).to_html()}
    </body>
    </html>
    """
    return html

# ==================== INTERFAZ PRINCIPAL ====================

st.title("⚡ UMM Analyzer Pro - Variador de Frecuencia")
st.markdown("---")

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("📂 Carga de archivo")
    
    archivo_subido = st.file_uploader(
        "Selecciona un archivo .umm",
        type=['umm', 'UMM', 'csv', 'txt'],
        help="Arrastra o selecciona un archivo .umm para analizar"
    )
    
    if archivo_subido is not None:
        st.success(f"✅ {archivo_subido.name}")
        st.info(f"📏 {archivo_subido.size:,} bytes")
        
        contenido = archivo_subido.read()
        hash_md5 = hashlib.md5(contenido).hexdigest()
        st.caption(f"🔐 MD5: {hash_md5[:16]}...")
        archivo_subido.seek(0)
        
        st.markdown("---")
        st.header("⚙️ Configuración")
        
        limite_muestras = st.slider(
            "Límite de muestras:",
            min_value=100,
            max_value=100000,
            value=50000,
            step=1000
        )
        
        aplicar_escalado_opt = st.checkbox("Aplicar escalado", value=True)
        
        if st.button("🚀 Procesar Archivo", type="primary"):
            st.session_state['procesar'] = True

# ==================== PROCESAMIENTO ====================

if archivo_subido is not None and st.session_state.get('procesar', False):
    try:
        contenido = archivo_subido.read()
        
        with st.spinner("🔍 Procesando archivo..."):
            datos_limpios, posiciones = extraer_datos_binarios(contenido, limite_muestras)
            
            df_crudo, num_filas = organizar_parametros(datos_limpios)
            
            if df_crudo is not None and num_filas > 0:
                if aplicar_escalado_opt:
                    df_mostrar = aplicar_escalado(df_crudo)
                else:
                    df_mostrar = df_crudo
                
                validacion = validar_datos(df_crudo)
                
                st.session_state['df_crudo'] = df_crudo
                st.session_state['df_mostrar'] = df_mostrar
                st.session_state['validacion'] = validacion
                st.session_state['archivo'] = archivo_subido.name
                st.session_state['hash'] = hash_md5
                st.session_state['num_filas'] = num_filas
                
                st.success("✅ Archivo procesado correctamente!")
                st.balloons()
            else:
                st.error("❌ No se pudieron organizar los datos")
                st.info("💡 Prueba con otro offset o verifica el archivo")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ==================== RESULTADOS ====================

if 'df_mostrar' in st.session_state:
    df_mostrar = st.session_state['df_mostrar']
    df_crudo = st.session_state['df_crudo']
    validacion = st.session_state.get('validacion', {})
    nombre_archivo = st.session_state.get('archivo', 'archivo')
    num_filas = st.session_state.get('num_filas', 0)
    
    st.subheader("🔍 Validación de Datos")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if validacion.get('valido', False):
            st.success("✅ DATOS CONFIABLES")
            st.metric("Nivel de confianza", f"{validacion.get('confianza', 0)}%")
        else:
            st.warning("⚠️ DATOS CON ADVERTENCIAS")
            st.metric("Nivel de confianza", f"{validacion.get('confianza', 0)}%")
    
    with col2:
        for msg in validacion.get('mensajes', []):
            if '✅' in msg:
                st.success(msg)
            elif '⚠️' in msg:
                st.warning(msg)
            else:
                st.info(msg)
    
    st.markdown("---")
    
    st.subheader("📊 Resumen del Archivo")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registros", f"{num_filas:,}")
    with col2:
        st.metric("Parámetros", len(NOMBRES_PARAM))
    with col3:
        st.metric("Escalado", "Aplicado" if aplicar_escalado_opt else "Sin escalar")
    with col4:
        st.metric("Archivo", nombre_archivo)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Dashboard", 
        "📊 Datos", 
        "📋 Estadísticas", 
        "🔗 Correlación",
        "📥 Exportar",
        "ℹ️ Información"
    ])
    
    with tab1:
        st.subheader("⚡ Dashboard del Variador")
        
        ultimo = df_mostrar.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🔵 Frecuencia", f"{ultimo['Frecuencia']:.2f} Hz")
            st.metric("🟢 Corriente", f"{ultimo['Corriente']:.3f} A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🔴 Voltaje", f"{ultimo['Voltaje']:.2f} V")
            st.metric("🟡 Potencia", f"{ultimo['Potencia']:.3f} kW")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("⚡ Velocidad", f"{ultimo['Velocidad']:.0f} RPM")
            st.metric("🔧 Torque", f"{ultimo['Torque']:.2f} Nm")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🌡️ Temperatura", f"{ultimo['Temperatura']:.0f} °C")
            st.metric("📊 Modo", f"{int(ultimo['Modo'])}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📈 Evolución de Parámetros")
        
        parametros_grafico = st.multiselect(
            "Selecciona parámetros para graficar:",
            df_mostrar.columns.tolist(),
            default=['Frecuencia', 'Corriente', 'Velocidad']
        )
        
        if parametros_grafico:
            fig = px.line(
                df_mostrar,
                y=parametros_grafico,
                title=f"Evolución de parámetros - {nombre_archivo}",
                labels={'index': 'Muestra', 'value': 'Valor', 'variable': 'Parámetro'}
            )
            fig.update_layout(height=450)
            fig.update_traces(line=dict(width=2))
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Distribución de Frecuencia")
        fig_hist = px.histogram(
            df_mostrar,
            x='Frecuencia',
            nbins=50,
            title="Distribución de frecuencia",
            labels={'Frecuencia': 'Frecuencia (Hz)'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab2:
        st.subheader("📋 Datos Completos")
        
        registros_mostrar = st.slider(
            "Registros a mostrar:",
            min_value=10,
            max_value=min(500, len(df_mostrar)),
            value=50
        )
        
        st.dataframe(df_mostrar.head(registros_mostrar), use_container_width=True)
        
        with st.expander("🔍 Valores de relleno filtrados"):
            st.write("**Valores considerados como relleno:**")
            for val in VALORES_RELLENO:
                st.code(f"• {val} (0x{val & 0xFFFF:04X})")
    
    with tab3:
        st.subheader("📊 Estadísticas Detalladas")
        
        st.dataframe(df_mostrar.describe(), use_container_width=True)
        
        st.subheader("📊 Estadísticas por Parámetro")
        estadisticas_df = calcular_estadisticas(df_mostrar)
        st.dataframe(estadisticas_df, use_container_width=True)
        
        st.subheader("📊 Percentiles")
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        df_percentiles = pd.DataFrame()
        for col in df_mostrar.columns:
            valores = [np.percentile(df_mostrar[col], p) for p in percentiles]
            df_percentiles[col] = valores
        df_percentiles.index = [f"{p}%" for p in percentiles]
        st.dataframe(df_percentiles, use_container_width=True)
    
    with tab4:
        st.subheader("🔗 Matriz de Correlación")
        
        if len(df_mostrar.columns) > 1:
            corr = df_mostrar.corr()
            
            fig_corr = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                title="Matriz de correlación entre parámetros",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1
            )
            fig_corr.update_layout(height=500)
            st.plotly_chart(fig_corr, use_container_width=True)
            
            st.subheader("📊 Tabla de Correlaciones")
            st.dataframe(corr, use_container_width=True)
        else:
            st.warning("⚠️ Se necesitan al menos 2 parámetros para correlación")
    
    with tab5:
        st.subheader("📥 Exportar Datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df_mostrar.to_csv(index=False)
            st.download_button(
                label="📥 CSV con escalado",
                data=csv,
                file_name=f"{nombre_archivo}_con_escalado.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            csv_crudo = df_crudo.to_csv(index=False)
            st.download_button(
                label="📥 CSV sin escalar",
                data=csv_crudo,
                file_name=f"{nombre_archivo}_sin_escalar.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            try:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_mostrar.to_excel(writer, sheet_name='Datos', index=False)
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Excel (.xlsx)",
                    data=excel_data,
                    file_name=f"{nombre_archivo}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except:
                st.warning("⚠️ Instala openpyxl para exportar a Excel")
        
        st.subheader("📄 Generar Reporte")
        if st.button("📄 Generar Reporte HTML"):
            html = generar_reporte_html(df_mostrar, nombre_archivo)
            st.download_button(
                label="📥 Descargar Reporte HTML",
                data=html,
                file_name=f"{nombre_archivo}_reporte.html",
                mime="text/html",
                use_container_width=True
            )
    
    with tab6:
        st.subheader("ℹ️ Información del Archivo")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Información General:**")
            st.write(f"- **Archivo:** {nombre_archivo}")
            st.write(f"- **Registros:** {num_filas:,}")
            st.write(f"- **Parámetros:** {len(NOMBRES_PARAM)}")
            st.write(f"- **Hash MD5:** {st.session_state.get('hash', 'N/A')[:16]}...")
        
        with col2:
            st.write("**Configuración de Escalado:**")
            df_factores = pd.DataFrame([
                {
                    'Parámetro': p,
                    'Factor': PARAMETROS[p]['factor'],
                    'Unidad': PARAMETROS[p]['unidad'],
                    'Rango': f"{PARAMETROS[p]['rango'][0]} - {PARAMETROS[p]['rango'][1]}"
                }
                for p in NOMBRES_PARAM
            ])
            st.dataframe(df_factores, use_container_width=True)
        
        st.subheader("🔍 Validación Detallada")
        for msg in validacion.get('mensajes', []):
            if '✅' in msg:
                st.success(msg)
            elif '⚠️' in msg:
                st.warning(msg)
            else:
                st.info(msg)
        
        if validacion.get('recomendaciones'):
            st.subheader("📌 Recomendaciones")
            for rec in validacion['recomendaciones']:
                st.info(f"💡 {rec}")

else:
    st.info("👈 **Sube un archivo en el panel lateral para comenzar**")
    
    st.markdown("""
    <div class="info-box">
        <h3>📋 ¿Cómo funciona?</h3>
        <ol>
            <li><b>Sube tu archivo</b> <code>.umm</code> desde el panel lateral</li>
            <li>La app <b>extrae automáticamente</b> los datos</li>
            <li><b>Escala</b> los valores según factores reales</li>
            <li><b>Valida</b> la integridad de los datos</li>
            <li><b>Visualiza</b> en gráficos interactivos</li>
            <li><b>Exporta</b> los datos a CSV, Excel o HTML</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Parámetros del Variador
        
        | Parámetro | Unidad | Factor |
        |-----------|--------|--------|
        | Frecuencia | Hz | ×0.01 |
        | Corriente | A | ×0.001 |
        | Voltaje | V | ×0.01 |
        | Velocidad | RPM | ×0.01 |
        | Potencia | kW | ×0.001 |
        | Torque | Nm | ×0.01 |
        """)
    
    with col2:
        st.markdown("""
        ### ✅ Datos de ejemplo
        
        Si tu archivo contiene:
        - **Frecuencia:** 1800 → 18.00 Hz
        - **Corriente:** 4352 → 4.352 A
        - **Voltaje:** 2922 → 29.22 V
        
        ¡Entonces el escalado es CORRECTO!
        """)

# ==================== FOOTER ====================
st.markdown("---")
st.caption(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("⚡ UMM Analyzer Pro v3.0 | Desarrollado con Streamlit")
