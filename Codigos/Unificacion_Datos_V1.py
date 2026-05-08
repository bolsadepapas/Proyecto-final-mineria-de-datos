import geopandas as gpd
import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore')

# Definimos los nombres reales de las columnas que vimos en tu JSON
COL_PAIS = 'country'
COL_ADMIN = 'name_field'

print("🌎 Iniciando proceso Pan-Amazónico...")

try:
    # Cargamos las capas base
    paises = gpd.read_file('national_admin.geojson')
    admin = gpd.read_file('admin_areas.geojson')
    protegidas = gpd.read_file('protected_areas.geojson')
    indigenas = gpd.read_file('indigenous_territories.geojson')

    # 1. LIMPIEZA CRUCIAL: Eliminamos filas que no sean países reales
    # Esto quita cualquier "Entire Amazon", "Amazon Basin" o "Total"
    paises = paises[paises['country'] != 'Entire Amazon']
    paises = paises[paises['country'] != 'Amazon Basin']
    paises = paises[paises['country'] != 'Total']
    # Si el nombre está en otra columna, asegúrate de filtrarla también
    paises = paises[paises['country'].notna()] 

    print(f"Países detectados tras limpieza: {paises['country'].unique()}")

    crs_comun = "EPSG:4326"
    paises = paises.to_crs(crs_comun)
    admin = admin.to_crs(crs_comun)
    protegidas = protegidas.to_crs(crs_comun)
    indigenas = indigenas.to_crs(crs_comun)
except Exception as e:
    print(f"❌ Error al cargar archivos base: {e}")
    exit()

archivos_anuales = {
    2018: 'amazon_basin_48px_v3.2-3.7ensemble_0.50_2018-01-01_2018-12-31-dissolved-0.6.geojson',
    2019: 'amazon_basin_48px_v3.2-3.7ensemble_0.50_2019-01-01_2019-12-31-dissolved-0.6.geojson',
    2020: 'amazon_basin_48px_v3.2-3.7ensemble_0.50_2020-01-01_2020-12-31-dissolved-0.6.geojson',
    2021: 'amazon_basin_48px_v3.2-3.7ensemble_0.50_2021-01-01_2021-12-31-dissolved-0.6.geojson',
    2022: 'amazon_basin_48px_v3.2-3.7ensemble_0.50_2022-01-01_2022-12-31-dissolved-0.6.geojson',
    2023: 'amazon_basin_48px_v3.2-3.7ensemble_0.50_2023-01-01_2023-12-31-dissolved-0.6.geojson',
    2024: 'amazon_basin_48px_v3.2-3.7ensemble_0.50_2024-01-01_2024-12-31-dissolved-0.6.geojson'
}

lista_final = []

for anio, nombre in archivos_anuales.items():
    if not os.path.exists(nombre):
        continue

    print(f"⌛ Procesando {anio}...")
    minas = gpd.read_file(nombre).to_crs(crs_comun)

    # Unión con Países
    res = gpd.sjoin(minas, paises[['geometry', COL_PAIS]], how='left', predicate='within')
    res = res.rename(columns={COL_PAIS: 'Pais'})

    # Unión con Áreas Administrativas
    if 'index_right' in res.columns: res = res.drop(columns='index_right')
    res = gpd.sjoin(res, admin[['geometry', COL_ADMIN]], how='left', predicate='within')
    res = res.rename(columns={COL_ADMIN: 'Region_Estado'})

    # Unión con Áreas Protegidas (asumiendo name_field)
    if 'index_right' in res.columns: res = res.drop(columns='index_right')
    res = gpd.sjoin(res, protegidas[['geometry', 'name_field']], how='left', predicate='within')
    res = res.rename(columns={'name_field': 'Area_Protegida'})

    # Unión con Indígenas (asumiendo name_field)
    if 'index_right' in res.columns: res = res.drop(columns='index_right')
    res = gpd.sjoin(res, indigenas[['geometry', 'name_field']], how='left', predicate='within')
    res = res.rename(columns={'name_field': 'Comunidad_Indigena'})

    # Cálculos finales
    res['Anio'] = anio
    res['Area_Ha'] = res.to_crs(epsg=3857).geometry.area / 10000
    res['Lat'] = res.geometry.centroid.y
    res['Lon'] = res.geometry.centroid.x

    cols = ['Anio', 'Pais', 'Region_Estado', 'Area_Protegida', 'Comunidad_Indigena', 'Area_Ha', 'Lat', 'Lon']
    lista_final.append(res[cols].copy())

if lista_final:
    master_df = pd.concat(lista_final, ignore_index=True)
    master_df.fillna("Sin registro").to_csv('MASTER_AMAZONIA_2018_2024.csv', index=False)
    print("✅ ¡LISTO! Tu base de datos de toda la Amazonía ha sido creada.")