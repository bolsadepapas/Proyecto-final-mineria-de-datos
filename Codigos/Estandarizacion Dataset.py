import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import json

# 1. Configuración de Datos Externos (Incentivo Económico)
oro_history = {
    2018: 1268, 2019: 1392, 2020: 1770, 
    2021: 1798, 2022: 1801, 2023: 1943, 2024: 2330
}

def procesar_mineria_pro():
    print("🚀 Iniciando Ingeniería de Datos Avanzada...")
    df = pd.read_csv('Genio1.csv')
    
    # Limpieza y preparación
    df = df.dropna(subset=['Lat', 'Lon', 'Anio'])
    df['Anio'] = df['Anio'].astype(int)
    
    # --- PARTE A: ANÁLISIS ECONÓMICO ---
    df['precio_oro'] = df['Anio'].map(oro_history)
    # Variación porcentual del oro respecto al año anterior
    df['incentivo_oro_pct'] = df['Anio'].apply(lambda x: (oro_history[x] - oro_history.get(x-1, x)) / oro_history.get(x-1, x) * 100)

    # --- PARTE B: ANÁLISIS ESPACIAL POR AÑO ---
    df_final = pd.DataFrame()
    
    for anio in sorted(df['Anio'].unique()):
        print(f"--- Procesando año {anio} ---")
        df_anio = df[df['Anio'] == anio].copy()
        coords = df_anio[['Lat', 'Lon']].values
        tree = cKDTree(coords)
        
        # 1. Distancia al vecino más cercano (Mismo año)
        dists, _ = tree.query(coords, k=2)
        df_anio['dist_vecino_km'] = dists[:, 1] * 111.32
        
        # 2. Densidad local (Radio de 10km)
        df_anio['densidad_10km'] = tree.query_ball_point(coords, r=0.09, return_length=True) - 1
        
        # 3. Distancia a Registro Oficial (Eficacia Gubernamental)
        # Separamos IA de Oficiales para medir el "vacío"
        df_ia = df_anio[df_anio['Validacion_Oficial'].str.contains('IA', na=False)]
        df_oficial = df_anio[df_anio['Deforestacion_Oficial'].str.contains('Registrado', na=False)]
        
        if not df_oficial.empty and not df_ia.empty:
            tree_oficial = cKDTree(df_oficial[['Lat', 'Lon']].values)
            dists_of, _ = tree_oficial.query(df_ia[['Lat', 'Lon']].values, k=1)
            # Mapeamos de vuelta al dataframe original del año
            df_anio.loc[df_ia.index, 'dist_a_oficial'] = dists_of * 111.32
        else:
            df_anio['dist_a_oficial'] = np.nan

        # 4. Clasificación de Riesgo
        df_anio['nivel_riesgo'] = np.where(
            (df_anio['densidad_10km'] > 5) & (df_anio['dist_a_oficial'] > 7), 
            'CRÍTICO (Sombra Estatal)', 
            'MODERADO'
        )

        df_final = pd.concat([df_final, df_anio])

    # --- PARTE C: ANÁLISIS TEMPORAL (PERSISTENCIA) ---
    # ¿Cuántas veces aparece este foco en un radio de 500m a lo largo de los años?
    print("--- Calculando Índice de Persistencia Temporal ---")
    all_coords = df_final[['Lat', 'Lon']].values
    master_tree = cKDTree(all_coords)
    # Buscamos puntos en un radio de ~500m (0.0045 grados)
    indices = master_tree.query_ball_point(all_coords, r=0.0045)
    df_final['indice_persistencia'] = [len(idx) for idx in indices]

    # --- PARTE D: EXPORTACIÓN ---
    df_final.to_csv('Genio2.csv', index=False)
    
    def to_geojson(df_data):
        features = []
        for _, row in df_data.iterrows():
            # Limpiar NaNs para el JSON
            props = row.fillna("N/A").to_dict()
            feature = {
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row['Lon']), float(row['Lat'])]
                }
            }
            features.append(feature)
        return {"type": "FeatureCollection", "features": features}

    with open('mapa_pro.geojson', 'w') as f:
        json.dump(to_geojson(df_final), f)

    print("✅ Procesamiento Completo. Variables creadas: dist_vecino, densidad, dist_a_oficial, indice_persistencia, incentivo_oro.")

if __name__ == "__main__":
    procesar_mineria_pro()