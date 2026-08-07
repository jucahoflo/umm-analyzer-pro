import struct
import os
import hashlib
from collections import Counter

def verificar_archivo(ruta):
    """Verifica la integridad y estructura del archivo"""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE INTEGRIDAD DEL ARCHIVO")
    print("=" * 60)
    
    # 1. Información básica
    tamaño = os.path.getsize(ruta)
    print(f"\n📏 Tamaño del archivo: {tamaño:,} bytes ({tamaño/1024/1024:.2f} MB)")
    
    # 2. Hash del archivo (para verificar que no cambia)
    with open(ruta, 'rb') as f:
        contenido = f.read()
        hash_md5 = hashlib.md5(contenido).hexdigest()
        hash_sha256 = hashlib.sha256(contenido).hexdigest()
    
    print(f"\n🔐 Hash MD5: {hash_md5}")
    print(f"🔐 Hash SHA256: {hash_sha256[:32]}...")
    
    # 3. Análisis de estructura
    print(f"\n📊 ANÁLISIS DE ESTRUCTURA:")
    print("-" * 40)
    
    # Primeros bytes
    primeros_20 = contenido[:20]
    print(f"Primeros 20 bytes (hex): {primeros_20.hex()}")
    print(f"Primeros 20 bytes (texto): {primeros_20}")
    
    # Buscar patrones
    patron_55 = contenido.count(b'\x55')
    patron_00 = contenido.count(b'\x00')
    patron_ff = contenido.count(b'\xff')
    
    print(f"\nPatrones encontrados:")
    print(f"  • 0x55 (U): {patron_55:,} ocurrencias ({patron_55/tamaño*100:.1f}%)")
    print(f"  • 0x00 (NUL): {patron_00:,} ocurrencias ({patron_00/tamaño*100:.1f}%)")
    print(f"  • 0xFF: {patron_ff:,} ocurrencias ({patron_ff/tamaño*100:.1f}%)")
    
    # 4. Extraer datos con diferentes métodos
    print(f"\n📊 EXTRACCIÓN DE DATOS:")
    print("-" * 40)
    
    # Método 1: Shorts (2 bytes) - nuestro método actual
    datos_shorts = []
    valores_unicos = set()
    for i in range(0, min(len(contenido), 100000), 2):
        try:
            val = struct.unpack('h', contenido[i:i+2])[0]
            if val != 21845 and val != 0:
                datos_shorts.append(val)
                valores_unicos.add(val)
        except:
            pass
    
    print(f"\n✅ Método SHORT (2 bytes):")
    print(f"  • Valores extraídos: {len(datos_shorts):,}")
    print(f"  • Valores únicos: {len(valores_unicos):,}")
    
    if datos_shorts:
        print(f"  • Rango: {min(datos_shorts)} a {max(datos_shorts)}")
        print(f"  • Promedio: {sum(datos_shorts)/len(datos_shorts):.2f}")
        
        # Verificar si hay valores que se repiten
        counter = Counter(datos_shorts)
        mas_comunes = counter.most_common(10)
        print(f"  • Valores más comunes: {mas_comunes[:5]}")
    
    # Método 2: Enteros (4 bytes)
    datos_ints = []
    for i in range(0, min(len(contenido), 100000), 4):
        try:
            val = struct.unpack('i', contenido[i:i+4])[0]
            if -100000 < val < 100000 and val != 0:
                datos_ints.append(val)
        except:
            pass
    
    print(f"\n✅ Método INT (4 bytes):")
    print(f"  • Valores extraídos: {len(datos_ints):,}")
    if datos_ints:
        print(f"  • Rango: {min(datos_ints)} a {max(datos_ints)}")
        print(f"  • Promedio: {sum(datos_ints)/len(datos_ints):.2f}")
    
    # 5. Verificación de consistencia
    print(f"\n✅ VERIFICACIÓN DE CONSISTENCIA:")
    print("-" * 40)
    
    # Verificar si los datos tienen sentido (rango razonable)
    if datos_shorts:
        rango_razonable = all(-10000 < v < 10000 for v in datos_shorts)
        print(f"  • ¿Todos los valores en rango razonable (-10000 a 10000)? {rango_razonable}")
        
        # Verificar si hay muchos valores repetidos
        if datos_shorts:
            repeticion = len(datos_shorts) / len(set(datos_shorts)) if set(datos_shorts) else 0
            print(f"  • Relación valores/únicos: {repeticion:.2f}")
            if repeticion < 1.5:
                print("    ✅ Baja repetición - Datos parecen variados")
            elif repeticion < 3:
                print("    ⚠️ Repetición moderada - Posibles datos de configuración")
            else:
                print("    ⚠️ Alta repetición - Posibles datos de relleno")
    
    # 6. Recomendación
    print(f"\n📋 RECOMENDACIÓN:")
    print("-" * 40)
    
    if len(datos_shorts) > 100 and len(datos_shorts) / len(contenido) * 100 > 10:
        print("✅ Los datos parecen ser válidos y contienen información significativa")
        print(f"   Se recomienda usar el método SHORT con offset 0")
    elif len(datos_shorts) > 0:
        print("⚠️ Los datos son limitados. Podrían ser configuración o cabecera")
        print("   Se recomienda verificar el offset o probar con otros tipos")
    else:
        print("❌ No se encontraron datos válidos. El archivo podría estar corrupto")
        print("   o tener un formato diferente")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        verificar_archivo(sys.argv[1])
    else:
        # Buscar automáticamente
        import glob
        archivos = glob.glob("umm/*.umm") + glob.glob("umm/*.UMM")
        if archivos:
            verificar_archivo(archivos[0])
        else:
            print("❌ No se encontraron archivos .umm")
