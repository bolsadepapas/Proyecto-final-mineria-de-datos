import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN # Algoritmo que usaremos para detectar grupos de puntos cercanos 
from sklearn.neighbors import BallTree
import os 



print("\n Cargando Genio1.csv (base)")

def cargar_datos():
    # Intenta varias rutas posibles
    rutas_posibles = [
        os.path.join('..', 'Dataset´s', 'Genio1.csv'),  # Con acento original (correcto)
    ]
    
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            print(f" Archivo encontrado en: {ruta}")
            return pd.read_csv(ruta)
    
    # Si no encuentra nada, muestra las rutas intentadas
    print("No se encontró el archivo en ninguna de estas ubicaciones:")
    for ruta in rutas_posibles:
        print(f"   - {ruta}")
    print("\n Verifica la ubicación del archivo Genio1.csv y ajusta la ruta.")
    raise FileNotFoundError("No se pudo localizar Genio1.csv")

df = cargar_datos()

print(f" Registros iniciales: {len(df)}")

# Coordenadas válidas
df = df.dropna(subset=['Lat', 'Lon'])

# Convertir tipos
df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
df['Area_Ha'] = pd.to_numeric(df['Area_Ha'], errors='coerce')
df['Anio'] = pd.to_numeric(df['Anio'], errors='coerce')

print("\n Normalizando logística aérea...")

def convertir_logistica(valor):
    valor = (
        str(valor)
        .strip()
        .lower()
    )
    negativos = [
        'sin pista cercana',
        'sin pista',
        'sin registro',
        'no registrada',
        'no detectada',
        'ninguna',
        'nan'
    ]
    for n in negativos:
        if n in valor:
            return 0
    return 1

# Reemplazamos la columna original
# por valores binarios (0/1)
# Esto mantiene UNA SOLA variable normalizada
df['Logistica_Aerea'] = (
    df['Logistica_Aerea']
    .apply(convertir_logistica)
)



print("\n Eliminando duplicados...")

antes = len(df)

df = df.drop_duplicates(
    subset=[
        'Anio',
        'Lat',
        'Lon',
        'Area_Ha'
    ]
)

despues = len(df)

print(f" Duplicados eliminados: {antes - despues}")


print("\n Integrando precio del oro...")

oro_history = {
    2018: 1268,
    2019: 1392,
    2020: 1770,
    2021: 1798,
    2022: 1801,
    2023: 1943,
    2024: 2330
}

serie_oro = pd.Series(oro_history).sort_index()

variacion_oro = (
    serie_oro.pct_change() * 100
).fillna(0)

df['precio_oro'] = df['Anio'].map(oro_history)

df['incentivo_oro_pct'] = (
    df['Anio']
    .map(variacion_oro)
)


print("\n Generando clusters espaciales...")

coords_rad = np.radians(
    df[['Lat', 'Lon']].values
)

kms_per_radian = 6371.0088 # Radio de la Tierra en km 

# 100 metros
epsilon = 0.1 / kms_per_radian # Convertir 100 metros a radianes

modelo = DBSCAN( # DBSCAN es un algoritmo de clustering que detecta grupos de puntos cercanos
    eps=epsilon,
    min_samples=1,
    metric='haversine', # Haversine es una fórmula que calcula la distancia entre dos puntos en la superficie de una esfera (como la Tierra) usando latitud y longitud
    algorithm='ball_tree' # BallTree es una estructura de datos eficiente que nos sirve para calcular distancias geoespaciales
)

df['cluster_id'] = modelo.fit_predict(
    coords_rad
)

print(
    f" Clusters detectados: "
    f"{df['cluster_id'].nunique()}" # nunique() cuenta el numero de valores unicos en la columna cluster_id
    # esto nos da el numero de clusters espaciales que se han formado
)


print("\n Calculando vecino más cercano...")

tree = BallTree( ## BallTree es una estructura de datos.... otra vez la usamos 
    coords_rad,
    metric='haversine' # Metrica para calcular distancias geoespaciales....
)

distancias, indices = tree.query(
    coords_rad,
    k=2
)

# Distancia al vecino más cercano
df['dist_vecino_km'] = (
    distancias[:, 1] * kms_per_radian
)


print("\n Calculando densidad espacial...")

radio_km = 10

radio_rad = radio_km / kms_per_radian # Convertir los 10 km a radianes para la consulta de vecinos

vecinos = tree.query_radius(
    coords_rad,
    r=radio_rad
)

df['densidad_10km'] = [
    len(v) - 1
    for v in vecinos
]



print("\n Calculando persistencia temporal...")

df = df.sort_values([
    'cluster_id',
    'Anio'
])

# Crecimiento
df['crecimiento_ha'] = (
    df.groupby('cluster_id')['Area_Ha']
    .diff()
    .fillna(0)
)

# Persistencia activa
# Mina considerada activa si:
# - Crecimiento significativo (expansión O contracción > 0.1 Ha)
# - O tiene logística aérea detectada (binaria: 0/1)
df['es_activa'] = (
    (
        abs(df['crecimiento_ha']) > 0.1
    ) |
    (
        df['Logistica_Aerea'] == 1
    )
)

# Índice acumulado
df['indice_persistencia'] = (
    df.groupby('cluster_id')['es_activa']
    .cumsum()
)


print("\n Calculando nivel de riesgo...")

def calcular_riesgo(row):

    score = 0

    # Áreas protegidas
    if row['Area_Protegida'] != 'Sin registro':
        score += 4

    # Comunidades indígenas
    if row['Comunidad_Indigena'] != 'Sin registro':
        score += 3

    # Deforestación oficial
    if str(row['Deforestacion_Oficial']).lower() != 'no registrado':
        score += 2

    # Alta densidad minera
    if row['densidad_10km'] >= 40:
        score += 2

    elif row['densidad_10km'] >= 15:
        score += 1

    # Persistencia alta
    if row['indice_persistencia'] >= 3:
        score += 2

    elif row['indice_persistencia'] >= 1:
        score += 1

    # Clasificación final
    if score >= 8:
        return 'CRÍTICO'

    elif score >= 5:
        return 'ALTO'

    elif score >= 3:
        return 'MODERADO'

    return 'BAJO'

df['nivel_riesgo'] = (
    df.apply(
        calcular_riesgo,
        axis=1
    )
)


## ordenamiento del dataset: columnas relevantes y orden lógico para el dashboard final

print("\n📚 Ordenando dataset...")

columnas_finales = [

    # TEMPORAL
    'Anio',

    # UBICACIÓN
    'Pais',
    'Region_Estado',
    'Lat',
    'Lon',

    # IDENTIFICACIÓN ESPACIAL
    'cluster_id',

    # CONTEXTO TERRITORIAL
    'Area_Protegida',
    'Comunidad_Indigena',

    # VARIABLES MINERAS
    'Area_Ha',
    'Logistica_Aerea',
    'Deforestacion_Oficial',

    # VALIDACIÓN
    'Validacion_Oficial',
    'Nivel_Confianza',

    # ECONOMÍA
    'precio_oro',
    'incentivo_oro_pct',

    # ESPACIAL
    'dist_vecino_km',
    'densidad_10km',

    # TEMPORAL
    'crecimiento_ha',
    'es_activa',
    'indice_persistencia',

    # RIESGO
    'nivel_riesgo'
]

# Mantener solo las columnas que existen
columnas_existentes = [
    c for c in columnas_finales
    if c in df.columns
]

df = df[columnas_existentes]



# Crear ruta de salida en la carpeta Dataset´s
carpeta_datasets = os.path.join('..', 'Dataset´s')


output_path = os.path.join(carpeta_datasets, 'Genio4_Final.csv')

df.to_csv(output_path, index=False)

print("\n" + "="*60)
print(" GENIO4 FINAL GENERADO")
print("="*60)

print(f" Archivo: {output_path}")