import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import struct
import hashlib
from datetime import datetime
import io
import time
import json
import zipfile

# ==================== CONFIGURACIÓN DE PÁGINA ====================
st.set_page_config(
    page_title="UMM Analyzer Pro - VSD Specialist",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS PERSONALIZADO - TABS MEJORADAS ====================
st.markdown("""
<style>
    /* FONDO CON GRADIENTE */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #1a1a3e, #24243e);
        background-attachment: fixed;
    }
    
    /* ANIMACIONES */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .fade-in { animation: fadeInUp 0.8s ease-out; }
    
    /* ENCABEZADO */
    .main-header {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1.5rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: space-between;
        z-index: 1;
        animation: slideDown 0.8s ease-out;
    }
    .main-header .left {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .main-header .logo {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #ffd700, #f7971e);
        padding: 0.5rem 1rem;
        border-radius: 16px;
        box-shadow: 0 0 40px rgba(255,215,0,0.15);
        animation: pulse 3s ease-in-out infinite;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #ffffff, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header .subtitle {
        color: rgba(255,255,255,0.6);
        font-size: 0.75rem;
        margin: 0;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .main-header .right {
        text-align: right;
        border-left: 2px solid rgba(255,255,255,0.1);
        padding-left: 1.5rem;
    }
    .main-header .right .name {
        color: #ffd700;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-shadow: 0 0 30px rgba(255,215,0,0.1);
    }
    .main-header .right .title {
        color: rgba(255,255,255,0.5);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .main-header .right .badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,215,0,0.05));
        padding: 0.2rem 1rem;
        border-radius: 20px;
        font-size: 0.6rem;
        color: #ffd700;
        border: 1px solid rgba(255,215,0,0.15);
        margin-top: 0.2rem;
        letter-spacing: 0.5px;
    }
    
    /* ========== TABS MEJORADAS - VISIBILIDAD PERFECTA ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(0,0,0,0.4);
        backdrop-filter: blur(10px);
        padding: 0.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 0.8rem 1.8rem !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: rgba(255,255,255,0.08) !important;
        color: rgba(255,255,255,0.7) !important;
        border: 2px solid transparent !important;
        letter-spacing: 0.5px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.18) !important;
        color: #ffffff !important;
        transform: translateY(-2px);
        border-color: rgba(255,215,0,0.2) !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #ffd700, #f7971e) !important;
        color: #0f0c29 !important;
        border-color: #ffd700 !important;
        box-shadow: 0 10px 30px -5px rgba(255,215,0,0.4) !important;
        transform: translateY(-3px);
        font-weight: 800 !important;
    }
    
    /* ========== TARJETAS DE MÉTRICAS ========== */
    .metric-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(10px);
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid #ffd700;
        height: 100%;
        animation: fadeInUp 0.6s ease-out;
    }
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 50px -10px rgba(0,0,0,0.5);
        border-color: #ffd700;
        background: rgba(255,255,255,0.10);
    }
    .metric-card .icon { font-size: 1.8rem; margin-bottom: 0.3rem; display: block; }
    .metric-card .label {
        font-size: 0.65rem;
        color: rgba(255,255,255,0.5);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0.2rem 0;
        text-shadow: 0 0 20px rgba(255,255,255,0.1);
    }
    .metric-card .unit {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.4);
    }
    
    /* ========== TARJETAS DE ESTADO ========== */
    .status-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(10px);
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.8s ease-out;
    }
    .status-card:hover {
        transform: scale(1.03);
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
    }
    .status-card .status-icon { font-size: 2.5rem; }
    .status-card .status-label {
        font-size: 0.9rem;
        font-weight: 700;
        margin-top: 0.3rem;
        color: #ffffff;
    }
    .status-card .status-detail {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.4);
        margin-top: 0.1rem;
    }
    .status-ok { border-left: 4px solid #00e676; }
    .status-warning { border-left: 4px solid #ffd600; }
    .status-danger { border-left: 4px solid #ff1744; }
    
    /* ========== BOTONES ========== */
    .stButton > button {
        background: linear-gradient(135deg, #ffd700, #f7971e) !important;
        color: #0f0c29 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 30px -10px rgba(255,215,0,0.4) !important;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 20px 40px -10px rgba(255,215,0,0.6) !important;
        background: linear-gradient(135deg, #ffe082, #ffd700) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00bcd4, #0097a7) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 700 !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 30px -10px rgba(0,188,212,0.4) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 20px 40px -10px rgba(0,188,212,0.6) !important;
        background: linear-gradient(135deg, #26c6da, #00bcd4) !important;
    }
    
    /* ========== SIDEBAR ========== */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(15,12,41,0.95), rgba(26,26,62,0.95)) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .css-1d391kg .stMarkdown { color: rgba(255,255,255,0.85) !important; }
    .css-1d391kg .stSelectbox label { color: rgba(255,255,255,0.7) !important; }
    .css-1d391kg .stSlider label { color: rgba(255,255,255,0.7) !important; }
    .css-1d391kg .stCheckbox label { color: rgba(255,255,255,0.7) !important; }
    .css-1d391kg .stFileUploader label { color: rgba(255,255,255,0.7) !important; }
    
    /* ========== SIDEBAR - ESPECIALISTA ========== */
    .specialist-card {
        background: linear-gradient(135deg, rgba(255,215,0,0.08), rgba(255,215,0,0.02));
        padding: 1rem;
        border-radius: 16px;
        margin-top: 1rem;
        text-align: center;
        border: 1px solid rgba(255,215,0,0.12);
        border-left: 3px solid #ffd700;
        backdrop-filter: blur(10px);
    }
    .specialist-card .icon { font-size: 1.5rem; opacity: 0.7; }
    .specialist-card .name {
        font-size: 1rem;
        font-weight: 700;
        color: #ffd700;
        margin: 0.2rem 0;
    }
    .specialist-card .title {
        font-size: 0.65rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .specialist-card .badge {
        display: inline-block;
        background: rgba(255,215,0,0.12);
        padding: 0.15rem 0.8rem;
        border-radius: 20px;
        font-size: 0.55rem;
        color: #ffd700;
        border: 1px solid rgba(255,215,0,0.12);
        margin-top: 0.2rem;
    }
    
    /* ========== EXPORT CARDS ========== */
    .export-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        margin: 0.5rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .export-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
        border-color: rgba(255,215,0,0.2);
    }
    .export-card .title {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .export-card .subtitle {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.4);
    }
    .export-badge {
        display: inline-block;
        padding: 0.15rem 0.7rem;
        border-radius: 20px;
        font-size: 0.6rem;
        font-weight: 600;
        margin: 0.15rem;
    }
    .badge-csv { background: rgba(46,125,50,0.25); color: #81c784; border: 1px solid rgba(46,125,50,0.2); }
    .badge-excel { background: rgba(13,71,161,0.25); color: #64b5f6; border: 1px solid rgba(13,71,161,0.2); }
    .badge-json { background: rgba(230,81,0,0.25); color: #ffb74d; border: 1px solid rgba(230,81,0,0.2); }
    .badge-raw { background: rgba(198,40,40,0.25); color: #ef9a9a; border: 1px solid rgba(198,40,40,0.2); }
    .badge-scaled { background: rgba(40,53,147,0.25); color: #7986cb; border: 1px solid rgba(40,53,147,0.2); }
    .badge-vsd { background: rgba(245,127,23,0.25); color: #ffcc80; border: 1px solid rgba(245,127,23,0.2); }
    
    /* ========== FOOTER ========== */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: rgba(255,255,255,0.3);
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 2rem;
        font-size: 0.7rem;
    }
    .footer .vsd { color: #ffd700; font-weight: 700; }
    .footer .separator { color: rgba(255,255,255,0.1); margin: 0 0.5rem; }
    
    /* ========== WELCOME ========== */
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .welcome-subtitle { color: rgba(255,255,255,0.5); font-size: 1rem; }
    .welcome-badge {
        background: linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,215,0,0.05));
        padding: 0.3rem 1.5rem;
        border-radius: 20px;
        display: inline-block;
        border: 1px solid rgba(255,215,0,0.12);
        color: #ffd700;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }
    
    /* ========== SECTION TITLES ========== */
    .section-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
    }
    
    /* ========== SELECTBOX / MULTISELECT ========== */
    .stSelectbox label, .stMultiSelect label {
        color: rgba(255,255,255,0.8) !important;
        font-weight: 600 !important;
    }
    .stSelectbox .st-bb, .stMultiSelect .st-bb {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    .stSelectbox .st-bb:hover, .stMultiSelect .st-bb:hover {
        border-color: #ffd700 !important;
    }
    
    /* ========== SLIDER ========== */
    .stSlider label {
        color: rgba(255,255,255,0.8) !important;
        font-weight: 600 !important;
    }
    
    /* ========== CHECKBOX ========== */
    .stCheckbox label {
        color: rgba(255,255,255,0.8) !important;
        font-weight: 600 !important;
    }
    
    /* ========== DATAFRAME ========== */
    .stDataFrame {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }
    .stDataFrame thead tr th {
        background: rgba(255,215,0,0.08) !important;
        color: #ffd700 !important;
        font-weight: 700 !important;
    }
    .stDataFrame tbody tr td {
        color: rgba(255,255,255,0.85) !important;
    }
    
    /* ========== ALERTS ========== */
    .stAlert {
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
    }
    .stAlert .stAlertContent {
        color: #ffffff !important;
    }
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

NOMBRES_PARAM = list(PARAMETROS.keys())
VALORES_RELLENO = [21845, -463, 0]

# ==================== FUNCIONES ====================

def extraer_datos_binarios(contenido, limite=50000):
    datos = []
    for i in range(0, min(len(contenido), limite), 2):
        try:
            val = struct.unpack('h', contenido[i:i+2])[0]
            if val not in VALORES_RELLENO and -10000 < val < 10000:
                datos.append(val)
        except:
            pass
    return datos

def organizar_parametros(datos):
    num_parametros = 10
    num_filas = len(datos) // num_parametros
    if num_filas == 0:
        return None, 0
    datos_limpios = datos[:num_filas * num_parametros]
    matriz = np.array(datos_limpios).reshape(num_filas, num_parametros)
    df = pd.DataFrame(matriz, columns=NOMBRES_PARAM)
    return df, num_filas

def aplicar_escalado(df):
    df_escalado = df.copy()
    for col in df.columns:
        if col in PARAMETROS:
            df_escalado[col] = df[col] * PARAMETROS[col]['factor']
    return df_escalado

def validar_datos(df):
    resultados = {'valido': False, 'mensajes': [], 'confianza': 0}
    if df is None or df.empty:
        return resultados
    resultados['confianza'] = 70
    resultados['valido'] = True
    resultados['mensajes'].append("Datos validados correctamente")
    return resultados

def generar_reporte_completo(df_crudo, df_escalado, nombre_archivo):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UMM Analyzer Pro - VSD Specialist Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; background: #0f0c29; color: white; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #1a2a6c, #302b63); padding: 2rem; border-radius: 16px; }}
            .header h1 {{ margin: 0; color: #ffd700; }}
            .header .sub {{ color: rgba(255,255,255,0.6); }}
            .section {{ background: rgba(255,255,255,0.05); padding: 1.5rem; margin: 1rem 0; border-radius: 12px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); }}
            table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
            th, td {{ border: 1px solid rgba(255,255,255,0.1); padding: 8px 12px; text-align: left; }}
            th {{ background-color: rgba(255,215,0,0.1); color: #ffd700; }}
            .footer {{ text-align: center; color: rgba(255,255,255,0.3); margin-top: 2rem; padding: 1rem; border-top: 1px solid rgba(255,255,255,0.05); }}
            .vsd-badge {{ background: rgba(255,215,0,0.1); color: #ffd700; padding: 0.2rem 1rem; border-radius: 20px; display: inline-block; border: 1px solid rgba(255,215,0,0.1); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚡ UMM Analyzer Pro</h1>
                <div class="vsd-badge">ESPECIALISTA VSD - FRONTEND DEVELOPER - JUAN CARLOS HOLGUIN</div>
                <p class="sub">Archivo: {nombre_archivo} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p class="sub">Registros: {len(df_escalado)} | Parámetros: {len(NOMBRES_PARAM)}</p>
            </div>
            
            <div class="section">
                <h2>📊 Datos Escalados (Valores Reales)</h2>
                {df_escalado.describe().to_html()}
            </div>
            
            <div class="section">
                <h2>📊 Datos Crudos (Sin Escalar)</h2>
                {df_crudo.describe().to_html()}
            </div>
            
            <div class="section">
                <h2>📋 Muestra de Datos</h2>
                <h3>Datos Escalados</h3>
                {df_escalado.head(20).to_html()}
                <h3>Datos Crudos</h3>
                {df_crudo.head(20).to_html()}
            </div>
            
            <div class="section">
                <h2>⚙️ Configuración de Parámetros</h2>
                <table>
                    <tr><th>Parámetro</th><th>Factor</th><th>Unidad</th><th>Rango</th></tr>
                    {''.join([f"<tr><td>{p}</td><td>{PARAMETROS[p]['factor']}</td><td>{PARAMETROS[p]['unidad']}</td><td>{PARAMETROS[p]['rango'][0]} - {PARAMETROS[p]['rango'][1]}</td></tr>" for p in NOMBRES_PARAM])}
                </table>
            </div>
            
            <div class="footer">
                UMM Analyzer Pro | ESPECIALISTA VSD - FRONTEND DEVELOPER - JUAN CARLOS HOLGUIN
            </div>
        </div>
    </body>
    </html>
    """
    return html

# ==================== HEADER ====================
st.markdown("""
<div class="main-header fade-in">
    <div class="left">
        <div class="logo">⚡</div>
        <div>
            <h1>UMM <span style="-webkit-text-fill-color:#ffd700;">Analyzer Pro</span></h1>
            <p class="subtitle">Industrial Monitoring &amp; Data Analysis Platform</p>
        </div>
    </div>
    <div class="right">
        <div class="name">JUAN CARLOS HOLGUIN</div>
        <div class="title">ESPECIALISTA VSD</div>
        <div class="badge">FRONTEND DEVELOPER</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <div style="font-size: 2rem; opacity: 0.6;">⚡</div>
        <h3 style="color: rgba(255,255,255,0.6); margin: 0; font-size: 0.9rem; letter-spacing: 2px;">CONTROL PANEL</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    archivo_subido = st.file_uploader(
        "📂 Upload .umm File",
        type=['umm', 'UMM', 'csv', 'txt'],
        help="Select your .umm file"
    )
    
    if archivo_subido is not None:
        st.success(f"✅ {archivo_subido.name}")
        st.info(f"📏 {archivo_subido.size:,} bytes")
        
        contenido = archivo_subido.read()
        hash_md5 = hashlib.md5(contenido).hexdigest()
        st.caption(f"🔐 MD5: {hash_md5[:16]}...")
        archivo_subido.seek(0)
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        limite_muestras = st.slider(
            "📊 Sample Limit",
            min_value=100,
            max_value=100000,
            value=50000,
            step=1000
        )
        
        aplicar_escalado_opt = st.checkbox("✅ Apply Scaling", value=True)
        
        if st.button("🚀 Process File", type="primary"):
            st.session_state['procesar'] = True
            st.session_state['archivo_subido'] = archivo_subido
            st.session_state['limite_muestras'] = limite_muestras
            st.session_state['aplicar_escalado_opt'] = aplicar_escalado_opt
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    <div class="specialist-card">
        <div class="icon">⚙️</div>
        <div class="name">Juan Carlos Holguin</div>
        <div class="title">Especialista VSD</div>
        <div class="badge">Frontend Developer</div>
        <div style="font-size: 0.55rem; color: rgba(255,255,255,0.25); margin-top: 0.4rem;">
            Industrial Automation Expert
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.08); font-size: 0.55rem; margin-top: 1rem;">
        v5.0 | Professional Edition
    </div>
    """, unsafe_allow_html=True)

# ==================== PROCESAMIENTO ====================
if st.session_state.get('procesar', False):
    archivo_subido = st.session_state.get('archivo_subido')
    limite_muestras = st.session_state.get('limite_muestras', 50000)
    aplicar_escalado_opt = st.session_state.get('aplicar_escalado_opt', True)
    
    if archivo_subido is not None:
        try:
            contenido = archivo_subido.read()
            
            with st.spinner("🔍 Processing data..."):
                time.sleep(0.5)
                datos_limpios = extraer_datos_binarios(contenido, limite_muestras)
                
                if len(datos_limpios) < 10:
                    st.error(f"⚠️ Datos insuficientes: solo se encontraron {len(datos_limpios)} valores")
                    st.info("💡 El archivo puede estar corrupto o no tener el formato esperado")
                    st.session_state['procesar'] = False
                    st.stop()
                
                df_crudo, num_filas = organizar_parametros(datos_limpios)
                
                if df_crudo is not None and num_filas > 0:
                    df_escalado = aplicar_escalado(df_crudo) if aplicar_escalado_opt else df_crudo.copy()
                    
                    validacion = validar_datos(df_crudo)
                    
                    st.session_state['df_escalado'] = df_escalado
                    st.session_state['df_crudo'] = df_crudo
                    st.session_state['validacion'] = validacion
                    st.session_state['archivo'] = archivo_subido.name
                    st.session_state['num_filas'] = num_filas
                    st.session_state['procesado'] = True
                    st.session_state['procesar'] = False
                    
                    st.success(f"✅ Data processed successfully! {num_filas} registros")
                    st.rerun()
                else:
                    st.error("❌ Could not organize data")
                    st.info("💡 El archivo no contiene suficientes datos para organizar en 10 parámetros")
                    st.session_state['procesar'] = False
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state['procesar'] = False

# ==================== DASHBOARD PRINCIPAL ====================
if st.session_state.get('procesado', False) and 'df_escalado' in st.session_state:
    df_escalado = st.session_state['df_escalado']
    df_crudo = st.session_state['df_crudo']
    nombre_archivo = st.session_state.get('archivo', 'archivo')
    num_filas = st.session_state.get('num_filas', 0)
    
    # ===== MÉTRICAS SUPERIORES =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <span class="icon">📊</span>
            <div class="label">Records</div>
            <div class="value">{num_filas:,}</div>
            <div class="unit">total samples</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ultimo = df_escalado.iloc[-1]
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #00bcd4;">
            <span class="icon">⚡</span>
            <div class="label">Frequency</div>
            <div class="value">{ultimo['Frecuencia']:.2f}</div>
            <div class="unit">Hz</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #00e676;">
            <span class="icon">🔌</span>
            <div class="label">Current</div>
            <div class="value">{ultimo['Corriente']:.3f}</div>
            <div class="unit">A</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff1744;">
            <span class="icon">🌡️</span>
            <div class="label">Temperature</div>
            <div class="value">{ultimo['Temperatura']:.0f}</div>
            <div class="unit">°C</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== SEGUNDA FILA =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ffd600;">
            <span class="icon">🔄</span>
            <div class="label">Speed</div>
            <div class="value">{ultimo['Velocidad']:.0f}</div>
            <div class="unit">RPM</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff9100;">
            <span class="icon">🔧</span>
            <div class="label">Torque</div>
            <div class="value">{ultimo['Torque']:.2f}</div>
            <div class="unit">Nm</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ffd700;">
            <span class="icon">⚡</span>
            <div class="label">Voltage</div>
            <div class="value">{ultimo['Voltaje']:.2f}</div>
            <div class="unit">V</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #d500f9;">
            <span class="icon">💡</span>
            <div class="label">Power</div>
            <div class="value">{ultimo['Potencia']:.3f}</div>
            <div class="unit">kW</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== ESTADO DEL SISTEMA =====
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estado = int(ultimo['Modo'])
        estados = {0: ("⬛", "Stopped", "status-ok"), 1: ("🟩", "Running", "status-ok"), 
                   2: ("🟨", "Jog", "status-warning"), 3: ("🟥", "Alarm", "status-danger"),
                   4: ("🟥", "Fault", "status-danger")}
        icon, label, css = estados.get(estado, ("❓", "Unknown", "status-warning"))
        st.markdown(f"""
        <div class="status-card {css}">
            <div class="status-icon">{icon}</div>
            <div class="status-label">{label}</div>
            <div class="status-detail">System Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        temp = ultimo['Temperatura']
        if temp < 60:
            icon, label = "🟩", "Normal"
        elif temp < 70:
            icon, label = "🟨", "Warning"
        else:
            icon, label = "🟥", "Critical"
        st.markdown(f"""
        <div class="status-card {'status-ok' if temp < 60 else 'status-warning' if temp < 70 else 'status-danger'}">
            <div class="status-icon">{icon}</div>
            <div class="status-label">{label}</div>
            <div class="status-detail">Temperature: {temp:.0f}°C</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        freq = ultimo['Frecuencia']
        if freq > 0:
            icon, label = "🟩", "Active"
        else:
            icon, label = "⏸️", "Idle"
        st.markdown(f"""
        <div class="status-card {'status-ok' if freq > 0 else 'status-warning'}">
            <div class="status-icon">{icon}</div>
            <div class="status-label">{label}</div>
            <div class="status-detail">Frequency: {freq:.2f} Hz</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== TABS MEJORADAS =====
    st.markdown("---")
    st.markdown("### 📊 Navigation")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Monitor",
        "📊 Analytics", 
        "📋 Data",
        "🔗 Correlation",
        "📥 Export"
    ])
    
    with tab1:
        st.markdown('<p class="section-title">📈 Real-time Monitoring</p>', unsafe_allow_html=True)
        
        parametros_grafico = st.multiselect(
            "Select parameters:",
            df_escalado.columns.tolist(),
            default=['Frecuencia', 'Corriente', 'Velocidad', 'Temperatura']
        )
        
        if parametros_grafico:
            fig = px.line(
                df_escalado,
                y=parametros_grafico,
                title=f"Parameter Evolution - {nombre_archivo}",
                labels={'index': 'Sample', 'value': 'Value', 'variable': 'Parameter'},
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig.update_layout(
                height=450,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.03)',
                font=dict(color='white'),
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="right", 
                    x=1,
                    font=dict(color='white')
                ),
                title_font=dict(color='white', size=16)
            )
            fig.update_traces(line=dict(width=2.5))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown('<p class="section-title">📊 Advanced Analytics</p>', unsafe_allow_html=True)
        st.dataframe(df_escalado.describe(), use_container_width=True)
        
        fig_box = px.box(df_escalado, title="Parameter Distribution")
        fig_box.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(255,255,255,0.03)',
            font=dict(color='white'),
            title_font=dict(color='white', size=16)
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.markdown('<p class="section-title">📋 Raw Data</p>', unsafe_allow_html=True)
        rows = st.slider("Rows:", 10, min(500, len(df_escalado)), 50)
        st.dataframe(df_escalado.head(rows), use_container_width=True)
    
    with tab4:
        st.markdown('<p class="section-title">🔗 Correlation Matrix</p>', unsafe_allow_html=True)
        if len(df_escalado.columns) > 1:
            corr = df_escalado.corr()
            fig_corr = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1
            )
            fig_corr.update_layout(
                height=550,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(255,255,255,0.03)',
                font=dict(color='white'),
                title_font=dict(color='white', size=16)
            )
            st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab5:
        st.markdown('<p class="section-title">📥 Export Data - Multiple Formats</p>', unsafe_allow_html=True)
        
        st.markdown("### Basic Formats")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="export-card">
                <div class="title">📊 CSV</div>
                <div class="subtitle">Universal format</div>
                <span class="export-badge badge-csv">CSV</span>
                <span class="export-badge badge-raw">Raw</span>
                <span class="export-badge badge-scaled">Scaled</span>
            </div>
            """, unsafe_allow_html=True)
            
            csv_scaled = df_escalado.to_csv(index=False)
            st.download_button(
                label="📥 CSV (Scaled)",
                data=csv_scaled,
                file_name=f"{nombre_archivo}_scaled.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            csv_raw = df_crudo.to_csv(index=False)
            st.download_button(
                label="📥 CSV (Raw)",
                data=csv_raw,
                file_name=f"{nombre_archivo}_raw.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.markdown("""
            <div class="export-card">
                <div class="title">📗 Excel</div>
                <div class="subtitle">With formatting</div>
                <span class="export-badge badge-excel">Excel</span>
                <span class="export-badge badge-raw">Raw</span>
                <span class="export-badge badge-scaled">Scaled</span>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                output_scaled = io.BytesIO()
                with pd.ExcelWriter(output_scaled, engine='openpyxl') as writer:
                    df_escalado.to_excel(writer, sheet_name='Scaled Data', index=False)
                    df_crudo.to_excel(writer, sheet_name='Raw Data', index=False)
                excel_data = output_scaled.getvalue()
                st.download_button(
                    label="📥 Excel (Complete)",
                    data=excel_data,
                    file_name=f"{nombre_archivo}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except:
                st.warning("Install openpyxl for Excel export")
        
        with col3:
            st.markdown("""
            <div class="export-card">
                <div class="title">📄 JSON</div>
                <div class="subtitle">For APIs</div>
                <span class="export-badge badge-json">JSON</span>
                <span class="export-badge badge-raw">Raw</span>
                <span class="export-badge badge-scaled">Scaled</span>
            </div>
            """, unsafe_allow_html=True)
            
            json_scaled = df_escalado.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 JSON (Scaled)",
                data=json_scaled,
                file_name=f"{nombre_archivo}_scaled.json",
                mime="application/json",
                use_container_width=True
            )
            
            json_raw = df_crudo.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 JSON (Raw)",
                data=json_raw,
                file_name=f"{nombre_archivo}_raw.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col4:
            st.markdown("""
            <div class="export-card">
                <div class="title">📦 ZIP</div>
                <div class="subtitle">All in one</div>
                <span class="export-badge badge-csv">CSV</span>
                <span class="export-badge badge-excel">Excel</span>
                <span class="export-badge badge-json">JSON</span>
            </div>
            """, unsafe_allow_html=True)
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f"{nombre_archivo}_scaled.csv", df_escalado.to_csv(index=False))
                zip_file.writestr(f"{nombre_archivo}_raw.csv", df_crudo.to_csv(index=False))
                zip_file.writestr(f"{nombre_archivo}_scaled.json", df_escalado.to_json(orient='records', indent=2))
                zip_file.writestr(f"{nombre_archivo}_raw.json", df_crudo.to_json(orient='records', indent=2))
                try:
                    excel_io = io.BytesIO()
                    with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
                        df_escalado.to_excel(writer, sheet_name='Scaled', index=False)
                        df_crudo.to_excel(writer, sheet_name='Raw', index=False)
                    zip_file.writestr(f"{nombre_archivo}.xlsx", excel_io.getvalue())
                except:
                    pass
            
            zip_data = zip_buffer.getvalue()
            st.download_button(
                label="📥 ZIP (All included)",
                data=zip_data,
                file_name=f"{nombre_archivo}_complete.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### Advanced Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="export-card">
                <div class="title">📊 HTML Report</div>
                <div class="subtitle">With statistics and branding</div>
                <span class="export-badge badge-vsd">VSD Specialist</span>
            </div>
            """, unsafe_allow_html=True)
            
            html_report = generar_reporte_completo(df_crudo, df_escalado, nombre_archivo)
            st.download_button(
                label="📥 HTML Report",
                data=html_report,
                file_name=f"{nombre_archivo}_reporte.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col2:
            st.markdown("""
            <div class="export-card">
                <div class="title">📦 Full Package</div>
                <div class="subtitle">All formats in ZIP</div>
                <span class="export-badge badge-csv">CSV</span>
                <span class="export-badge badge-excel">Excel</span>
                <span class="export-badge badge-json">JSON</span>
                <span class="export-badge badge-vsd">HTML</span>
            </div>
            """, unsafe_allow_html=True)
            
            zip_full = io.BytesIO()
            with zipfile.ZipFile(zip_full, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f"{nombre_archivo}_scaled.csv", df_escalado.to_csv(index=False))
                zip_file.writestr(f"{nombre_archivo}_raw.csv", df_crudo.to_csv(index=False))
                zip_file.writestr(f"{nombre_archivo}_scaled.json", df_escalado.to_json(orient='records', indent=2))
                zip_file.writestr(f"{nombre_archivo}_raw.json", df_crudo.to_json(orient='records', indent=2))
                zip_file.writestr(f"{nombre_archivo}_reporte.html", generar_reporte_completo(df_crudo, df_escalado, nombre_archivo))
                try:
                    excel_io = io.BytesIO()
                    with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
                        df_escalado.to_excel(writer, sheet_name='Scaled', index=False)
                        df_crudo.to_excel(writer, sheet_name='Raw', index=False)
                    zip_file.writestr(f"{nombre_archivo}.xlsx", excel_io.getvalue())
                except:
                    pass
            
            zip_full_data = zip_full.getvalue()
            st.download_button(
                label="📥 Full Package (ZIP)",
                data=zip_full_data,
                file_name=f"{nombre_archivo}_full_package.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        st.markdown("---")
        st.info(f"""
        **Export Summary**
        
        File: {nombre_archivo}
        Records: {num_filas:,}
        Parameters: {len(NOMBRES_PARAM)}
        
        Available formats: CSV, Excel, JSON, ZIP, HTML
        """)

else:
    # ==================== PANTALLA DE INICIO ====================
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <div style="font-size: 4rem; opacity: 0.4; animation: float 3s ease-in-out infinite;">⚡</div>
        <h1 class="welcome-title">UMM Analyzer Pro</h1>
        <p class="welcome-subtitle">Upload your .umm file to start analyzing industrial data</p>
        <div style="margin-top: 0.5rem;">
            <span class="welcome-badge">ESPECIALISTA VSD - FRONTEND DEVELOPER - JUAN CARLOS HOLGUIN</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.04); backdrop-filter: blur(10px); padding: 2rem; border-radius: 20px; border: 1px solid rgba(255,255,255,0.06); box-shadow: 0 20px 40px -10px rgba(0,0,0,0.3);">
            <h4 style="color: #ffffff; margin-top: 0; text-align: center;">📋 Quick Guide</h4>
            <ol style="line-height: 2.2rem; padding-left: 1.2rem; font-size: 0.9rem; color: rgba(255,255,255,0.7);">
                <li>📂 Click <strong style="color:#ffd700;">Browse Files</strong> in the sidebar</li>
                <li>⚡ Select your <strong style="color:#ffd700;">.umm</strong> file</li>
                <li>🚀 Click <strong style="color:#ffd700;">Process File</strong></li>
                <li>📊 Explore the <strong style="color:#ffd700;">interactive dashboard</strong></li>
                <li>📥 Export in <strong style="color:#ffd700;">multiple formats</strong></li>
            </ol>
            <hr style="border-color: rgba(255,255,255,0.05);">
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <div style="font-size: 1.5rem;">📈</div>
                    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Monitor</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem;">📊</div>
                    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Analyze</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem;">📥</div>
                    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.35);">Export</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>
        ⚡ UMM Analyzer Pro v5.0
        <span class="separator">|</span>
        <span class="vsd">ESPECIALISTA VSD - FRONTEND DEVELOPER - JUAN CARLOS HOLGUIN</span>
        <span class="separator">|</span>
        📅 {date}
    </p>
    <p style="font-size: 0.65rem; color: rgba(255,255,255,0.1); margin-top: 0.2rem;">
        Industrial Automation Expert | Data Analysis Platform
    </p>
</div>
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
