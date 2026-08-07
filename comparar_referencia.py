import pandas as pd
import numpy as np

print("📊 COMPARACIÓN CON DATOS DE REFERENCIA")
print("=" * 60)

# Cargar datos extraídos
try:
    df = pd.read_csv('datos_reales.csv')
    datos = df['Valor'].tolist()
    
    print(f"\n📋 DATOS EXTRAÍDOS:")
    print(f"  • Total: {len(datos):,} registros")
    print(f"  • Rango: {min(datos)} a {max(datos)}")
    print(f"  • Promedio: {sum(datos)/len(datos):.2f}")
    print(f"  • Únicos: {len(set(datos))}")
    
    # Comparar con valores típicos de variador
    print(f"\n🔍 VERIFICACIÓN CON PARÁMETROS TÍPICOS:")
    print("-" * 40)
    
    # Valores típicos para variador
    rangos = {
        'Frecuencia': (0, 5000),  # 0-50 Hz
        'Corriente': (0, 10000),  # 0-10 A
        'Temperatura': (0, 1000),  # 0-100°C
        'Velocidad': (0, 6000),   # 0-6000 RPM
        'Torque': (-10000, 10000),
        'Voltaje': (0, 10000),    # 0-1000V
    }
    
    # Verificar si los datos caen en rangos típicos
    en_rango = []
    for nombre, (min_val, max_val) in rangos.items():
        count = sum(1 for v in datos if min_val <= v <= max_val)
        porcentaje = count / len(datos) * 100
        en_rango.append((nombre, porcentaje))
        print(f"  • {nombre}: {porcentaje:.1f}% en rango ({min_val}-{max_val})")
    
    # Determinar si es un variador
    if any(p > 80 for _, p in en_rango):
        print(f"\n✅ Los datos parecen ser de un VARIADOR DE FRECUENCIA")
    else:
        print(f"\n⚠️ Los datos NO corresponden a un variador típico")
        print(f"   Podrían ser configuración o datos de otro equipo")
    
except Exception as e:
    print(f"❌ Error: {e}")
