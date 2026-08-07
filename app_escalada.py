import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import struct

st.set_page_config(page_title="Variador - Datos con Escalado", layout="wide")
st.title("⚡ Variador de Frecuencia - Datos con Escalado")

# Configuración de parámetros
PARAMETROS = {
    'Modo': {'factor': 1, 'unidad': '', 'decimales': 0},
    'Frecuencia': {'factor': 0.01, 'unidad': 'Hz', 'decimales': 2},
    'Corriente': {'factor': 0.001, 'unidad': 'A', 'decimales': 3},
    'Temperatura': {'factor': 1, 'unidad': '°C', 'decimales': 0},
    'Velocidad': {'factor': 0.01, 'unidad': 'RPM', 'decimales': 0},
    'Torque': {'factor': 0.01, 'unidad': 'Nm', 'decimales': 2},
    'Voltaje': {'factor': 0.01, 'unidad': 'V', 'decimales': 2},
    'Potencia': {'factor': 0.001, 'unidad': 'kW', 'decimales': 3},
    'Factor_Potencia': {'factor': 0.001, 'unidad': '', 'decimales': 3},
    'Estado': {'factor': 1, 'unidad': '', 'decimales': 0}
}

def extraer_datos(contenido):
    """Extrae datos del archivo .umm"""
    datos = []
    for i in range(0, min(len(contenido), 50000), 2):
        try:
            val = struct.unpack('h', contenido[i:i+2])[0]
            if val != 21845 and val != 0 and -10000 < val < 10000:
                datos.append(val)
        except:
            pass
    return datos

def aplicar_escalado(df, parametros):
    """Aplica escalado a los datos"""
    df_escalado = df.copy()
    
    for col in df.columns:
        if col in parametros:
            factor = parametros[col]['factor']
            df_escalado[col] = df[col] * factor
    
    return df_escalado

# Sidebar
with st.sidebar:
    st.header("📂 Carga de archivo")
    
    archivo = st.file_uploader(
        "Selecciona un archivo .umm",
        type=['umm', 'UMM']
    )
    
    if archivo:
        st.success(f"✅ {archivo.name}")
        
        # Opciones de escalado
        st.markdown("---")
        st.header("⚙️ Escalado")
        
        aplicar_escalado_opt = st.checkbox("Aplicar escalado automático", value=True)
        
        if st.button("🚀 Procesar", type="primary"):
            contenido = archivo.read()
            datos = extraer_datos(contenido)
            
            # Organizar en 10 parámetros
            num_parametros = 10
            num_filas = len(datos) // num_parametros
            
            if num_filas > 0:
                matriz = np.array(datos[:num_filas * num_parametros]).reshape(num_filas, num_parametros)
                
                nombres = ['Modo', 'Frecuencia', 'Corriente', 'Temperatura', 
                          'Velocidad', 'Torque', 'Voltaje', 'Potencia', 
                          'Factor_Potencia', 'Estado']
                
                df = pd.DataFrame(matriz, columns=nombres)
                
                # Guardar en sesión
                st.session_state['df_crudo'] = df
                st.session_state['archivo'] = archivo.name
                st.session_state['aplicar_escalado'] = aplicar_escalado_opt
                
                st.success(f"✅ {len(df)} registros procesados")
            else:
                st.error("❌ No se pudieron organizar los datos")

# Mostrar resultados
if 'df_crudo' in st.session_state:
    df_crudo = st.session_state['df_crudo']
    archivo = st.session_state['archivo']
    aplicar = st.session_state.get('aplicar_escalado', True)
    
    # Aplicar escalado
    if aplicar:
        df_mostrar = aplicar_escalado(df_crudo, PARAMETROS)
        titulo = "📊 Datos con ESCALADO aplicado"
    else:
        df_mostrar = df_crudo
        titulo = "📊 Datos CRUDOS (sin escalado)"
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "📊 Datos", "📋 Estadísticas", "📥 Exportar"])
    
    with tab1:
        st.subheader("📊 Dashboard del Variador")
        
        # Estado actual
        ultimo = df_mostrar.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔵 Frecuencia", f"{ultimo['Frecuencia']:.2f} Hz")
            st.metric("🟢 Corriente", f"{ultimo['Corriente']:.3f} A")
        with col2:
            st.metric("🔴 Voltaje", f"{ultimo['Voltaje']:.2f} V")
            st.metric("🟡 Potencia", f"{ultimo['Potencia']:.3f} kW")
        with col3:
            st.metric("⚡ Velocidad", f"{ultimo['Velocidad']:.0f} RPM")
            st.metric("🔧 Torque", f"{ultimo['Torque']:.2f} Nm")
        with col4:
            st.metric("🌡️ Temperatura", f"{ultimo['Temperatura']:.0f} °C")
            st.metric("📊 Modo", f"{int(ultimo['Modo'])}")
        
        # Gráficos
        st.subheader("📈 Evolución de parámetros")
        
        parametros_grafico = st.multiselect(
            "Selecciona parámetros:",
            df_mostrar.columns.tolist(),
            default=['Frecuencia', 'Corriente', 'Velocidad']
        )
        
        if parametros_grafico:
            fig = px.line(df_mostrar, y=parametros_grafico,
                         title=f"Evolución de parámetros - {archivo}")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar valores actuales en tabla
        st.subheader("📊 Valores actuales")
        st.dataframe(ultimo.to_frame('Valor Actual'), use_container_width=True)
    
    with tab2:
        st.subheader("📋 Datos completos")
        
        # Mostrar con formato
        st.dataframe(df_mostrar, use_container_width=True)
        
        # Mostrar factor de escalado
        with st.expander("ℹ️ Factores de escalado aplicados"):
            df_factores = pd.DataFrame([
                {'Parámetro': p, 'Factor': PARAMETROS[p]['factor'], 'Unidad': PARAMETROS[p]['unidad']}
                for p in df_mostrar.columns
            ])
            st.dataframe(df_factores, use_container_width=True)
    
    with tab3:
        st.subheader("📊 Estadísticas")
        
        # Estadísticas descriptivas
        st.dataframe(df_mostrar.describe(), use_container_width=True)
        
        # Correlación
        st.subheader("🔗 Correlación entre parámetros")
        if len(df_mostrar.columns) > 1:
            corr = df_mostrar.corr()
            fig_corr = px.imshow(corr, text_auto=True, aspect="auto")
            st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab4:
        st.subheader("📥 Exportar datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exportar con escalado
            csv_escalado = df_mostrar.to_csv(index=False)
            st.download_button(
                label="📥 Descargar con escalado (CSV)",
                data=csv_escalado,
                file_name=f"{archivo}_con_escalado.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Exportar crudo
            csv_crudo = df_crudo.to_csv(index=False)
            st.download_button(
                label="📥 Descargar datos crudos (CSV)",
                data=csv_crudo,
                file_name=f"{archivo}_crudo.csv",
                mime="text/csv",
                use_container_width=True
            )

else:
    st.info("👈 Sube un archivo .umm en el panel lateral")
    
    with st.expander("📖 Explicación del escalado"):
        st.markdown("""
        ### 📊 Escalado de datos del variador
        
        Los datos del variador se almacenan como números enteros (shorts) y necesitan escalado:
        
        | Parámetro | Factor | Ejemplo |
        |-----------|--------|---------|
        | Frecuencia | × 0.01 | 1800 → 18.00 Hz |
        | Corriente | × 0.001 | 4352 → 4.352 A |
        | Voltaje | × 0.01 | 2922 → 29.22 V |
        | Velocidad | × 0.01 | 3941 → 39.41 RPM |
        | Potencia | × 0.001 | 4457 → 4.457 kW |
        | Torque | × 0.01 | -6646 → -66.46 Nm |
        
        ### ✅ ¿Cómo saber si el escalado es correcto?
        
        Si ves valores como:
        - Frecuencia: 1800 → **18.00 Hz** (coherente)
        - Corriente: 4352 → **4.35 A** (coherente)
        - Voltaje: 2922 → **29.22 V** (coherente)
        
        ¡Entonces el escalado es CORRECTO!
        """)
