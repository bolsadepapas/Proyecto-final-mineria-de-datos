import pandas as pd

def implementar_persistencia_activa(df):
    print("🔄 Analizando dinámica de crecimiento para validar persistencia...")

    # 1. Crear una clave única por ubicación (redondeando coordenadas)
    # Esto agrupa puntos que están en el mismo lugar físico
    df['coord_key'] = df['Lat'].round(3).astype(str) + "_" + df['Lon'].round(3).astype(str)

    # 2. Ordenar cronológicamente para comparar año tras año
    df = df.sort_values(['coord_key', 'Anio'])

    # 3. Calcular la diferencia de área (Delta Area)
    # Compara el Area_Ha del año actual con el anterior del mismo grupo (coord_key)
    df['crecimiento_ha'] = df.groupby('coord_key')['Area_Ha'].diff().fillna(0)

    # 4. Definir si la persistencia es ACTIVA
    # Es activa si el hueco creció más de 0.1 hectáreas O si se detectó logística (pista/maquinaria)
    df['es_activa'] = (df['crecimiento_ha'] > 0.1) | (df['Logistica_Aerea'] == 1)

    # 5. Generar el Índice de Persistencia Real
    # Cumsum() suma 1 cada vez que 'es_activa' es True para ese grupo de coordenadas
    df['indice_persistencia'] = df.groupby('coord_key')['es_activa'].cumsum()

    # 6. Limpieza: Si un punto no tiene crecimiento ni logística, su persistencia no sube
    # Esto evita que un "hueco viejo" abandonado puntúe alto.
    return df

# --- APLICACIÓN EN TU FLUJO ---
df = pd.read_csv('Genio2.1.csv')
# (Aquí irían tus otras limpiezas de 0 y 1)
df = implementar_persistencia_activa(df)
df.to_csv('Genio2.1.1.csv', index=False)
print("✅ Índice de persistencia corregido basado en crecimiento de área.")