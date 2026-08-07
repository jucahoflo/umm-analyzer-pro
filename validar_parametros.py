import struct
import pandas as pd
import numpy as np
from collections import Counter

def analizar_estructura(ruta):
    """Analiza la estructura real del archivo"""
    
    with open(ruta, 'rb') as f:
        contenido = f.read()
    
    print("=" * 70)
    print("🔍 ANÁLISIS DE ESTRUCTURA DE DATOS")
    print("=" * 70)
    
    # 1. Buscar patrones de repetición
    print("\n📊 PATRONES DE REPETICIÓN:")
    print("-" * 40)
    
    # Contar valores comunes
    valores = []
    for i in range(0, min(len(contenido), 2000), 2):
        try:
            val = struct.unpack('h', contenido[i:i+2])[0]
            valores.append(val)
        except:
            pass
    
    counter = Counter(valores)
    print("Valores más frecuentes:")
    for val, count in counter.most_common(10):
        print(f"  {val}: {count} veces ({count/len(valores)*100:.1f}%)")
    
    # 2. Buscar estructura de 10
    print("\n📊 ESTRUCTURA DE BLOQUES:")
    print("-" * 40)
    
    # Probar diferentes tamaños de bloque
    for bloque_size in [8, 10, 12, 16, 20]:
        if len(valores) % bloque_size == 0:
            print(f"  ✅ Los datos son divisibles en bloques de {bloque_size}")
    
    # 3. Verificar si hay un offset correcto
    print("\n📊 BUSCANDO OFFSET CORRECTO:")
    print("-" * 40)
    
    for offset in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:
        muestra = []
        for i in range(offset, offset + 20, 2):
            try:
                val = struct.unpack('h', contenido[i:i+2])[0]
                muestra.append(val)
            except:
                pass
        
        # Verificar si este offset produce valores razonables
        no_cero = [v for v in muestra if v != 0 and v != 21845]
        if no_cero:
            print(f"  Offset {offset}: {no_cero[:5]}... ({len(no_cero)} valores no-cero)")
        else:
            print(f"  Offset {offset}: Solo ceros o relleno")

if __name__ == "__main__":
    import glob
    archivos = glob.glob("umm/*.umm") + glob.glob("umm/*.UMM")
    if archivos:
        analizar_estructura(archivos[0])
    else:
        print("❌ No se encontraron archivos .umm")
