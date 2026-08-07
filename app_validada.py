import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import struct
import hashlib
from collections import Counter
import io

st.set_page_config(page_title="UMM Analyzer - Validación", layout="wide")

st.title("🔍 UMM Analyzer - Extracción Validada")
st.markdown("---")

# Función de validación
def validar_datos(datos, nombre_archivo):
    """Valida la calidad de los datos extraídos"""
    
    resultados = {
        'valido': False,
        'mensajes': [],
        'estadisticas': {},
        'recomendaciones': []
    }
    
    if not datos:
        resultados['mensajes'].append("❌ No se encontraron datos")
        return resultados
    
    # Estadísticas básicas
    resultados['estadisticas']['total'] = len(datos)
    resultados['estadisticas']['min'] = min(datos)
    resultados['estadisticas']['max'] = max(datos)
    resultados['estadisticas']['promedio'] = sum(datos) / len(datos)
    resultados['estadisticas']['unicos'] = len(set(datos))
    
    # Verificación 1: Rango razonable
    if all(-10000 < v < 10000 for v in datos):
        resultados['mensajes'].append("✅ Rango de valores razonable")
    else:
        resultados['mensajes'].append("⚠️ Valores fuera de rango esperado")
        resultados['recomendaciones'].append("Verificar el offset o el tipo de dato")
    
    # Verificación 2: Diversidad de datos
    relacion = len(datos) / len(set(datos)) if set(datos) else 0
    if relacion < 1.5:
        resultados['mensajes'].append("✅ Datos variados y no repetitivos")
    elif relacion < 3:
        resultados['mensajes'].append("⚠️ Datos con repetición moderada")
        resultados['recomendaciones'].append("Podrían ser datos de configuración")
    else:
        resultados['mensajes'].append("⚠️ Alta repetición de valores")
        resultados['recomendaciones'].append("Posiblemente datos de relleno. Probar otro offset")
    
    # Verificación 3: Cantidad de datos
    if len(datos) > 100:
        resultados['mensajes'].append(f"✅ Suficientes datos ({len(datos):,} registros)")
    else:
        resultados['mensajes'].append(f"⚠️ Pocos datos ({len(datos)} registros)")
        resultados['recomendaciones'].append("El archivo podría ser solo una cabecera")
    
    # Verificación 4: Valores nulos/cero
    ceros = sum(1 for v in datos if v == 0)
    if ceros / len(datos) < 0.3:
        resultados['mensajes'].append(f"✅ Pocos valores cero ({ceros/len(datos)*100:.1f}%)")
    else:
        resultados['mensajes'].append(f"⚠️ Muchos valores cero ({ceros/len(datos)*100:.1f}%)")
        resultados['recomendaciones'].append("Verificar el offset de lectura")
    
    # Determinar si es válido
    if len(resultados['recomendaciones']) == 0:
        resultados['valido'] = True
        resultados['mensajes'].append("✅ DATOS VALIDADOS CONFIABLES")
    else:
        resultados['valido'] = False
    
    return resultados

# Sidebar
with st.sidebar:
    st.header("📂 Carga de archivo")
    
    archivo_subido = st.file_uploader(
        "Selecciona un archivo .umm",
        type=['umm', 'UMM', 'csv', 'txt']
    )
    
    if archivo_subido:
        st.success(f"✅ Archivo: {archivo_subido.name}")
        
        # Calcular hash
        contenido = archivo_subido.read()
        hash_md5 = hashlib.md5(contenido).hexdigest()
        st.info(f"🔐 MD5: {hash_md5[:16]}...")
        
        # Resetear el puntero del archivo
        archivo_subido.seek(0)
        
        if st.button("🔍 Validar y Extraer", type="primary"):
            st.session_state['procesar'] = True

# Procesamiento
if archivo_subido and st.session_state.get('procesar', False):
    try:
        contenido = archivo_subido.read()
        
        with st.spinner("🔍 Extrayendo y validando datos..."):
            # Extraer datos
            datos = []
            for i in range(0, min(len(contenido), 50000), 2):
                try:
                    val = struct.unpack('h', contenido[i:i+2])[0]
                    if val != 21845 and val != 0 and -10000 < val < 10000:
                        datos.append(val)
                except:
                    pass
            
            # Validar
            validacion = validar_datos(datos, archivo_subido.name)
            
            # Guardar en sesión
            st.session_state['datos'] = datos
            st.session_state['validacion'] = validacion
            st.session_state['archivo'] = archivo_subido.name
            
            if validacion['valido']:
                st.success("✅ Datos extraídos y validados correctamente!")
                st.balloons()
            else:
                st.warning("⚠️ Datos extraídos con advertencias")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Mostrar resultados
if 'datos' in st.session_state:
    datos = st.session_state['datos']
    validacion = st.session_state.get('validacion', {})
    nombre = st.session_state.get('archivo', 'archivo')
    
    # Mostrar validación
    st.subheader("📋 Validación de Datos")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if validacion.get('valido', False):
            st.success("✅ DATOS CONFIABLES")
        else:
            st.warning("⚠️ DATOS CON ADVERTENCIAS")
    
    with col2:
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
    
    st.markdown("---")
    
    # Mostrar datos
    if datos:
        df = pd.DataFrame({
            'Índice': range(len(datos)),
            'Valor': datos
        })
        
        # Estadísticas
        st.subheader("📊 Estadísticas de los datos")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", f"{len(datos):,}")
        with col2:
            st.metric("Mínimo", f"{min(datos):.2f}")
        with col3:
            st.metric("Máximo", f"{max(datos):.2f}")
        with col4:
            st.metric("Promedio", f"{sum(datos)/len(datos):.2f}")
        
        # Tabla
        st.subheader("📋 Datos extraídos")
        st.dataframe(df.head(100), use_container_width=True)
        
        # Gráfico
        st.subheader("📈 Visualización")
        fig = px.line(df, x='Índice', y='Valor',
                     title=f"Datos extraídos de {nombre}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Descargar
        st.subheader("📥 Exportar")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"{nombre}_validado.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No se encontraron datos")

else:
    st.info("👈 Sube un archivo en el panel lateral")
    
    with st.expander("📖 ¿Cómo saber si los datos son confiables?"):
        st.markdown("""
        ### 🔍 Verificaciones automáticas:
        
        1. **Rango de valores**: Los datos deben estar en un rango razonable
        2. **Diversidad**: Los valores no deben ser todos iguales
        3. **Cantidad**: Debe haber suficientes datos para análisis
        4. **Patrones**: No debe haber solo datos de relleno (0x55)
        
        ### 📊 Indicadores de datos confiables:
        - ✅ Valores entre -10000 y 10000
        - ✅ Más de 100 datos extraídos
        - ✅ Baja repetición de valores
        - ✅ Distribución variada
        
        ### ⚠️ Indicadores de datos no confiables:
        - ❌ Todos los valores son iguales
        - ❌ Solo valores 0 o 21845
        - ❌ Menos de 10 datos extraídos
        - ❌ Valores extremos (>100000)
        """)
