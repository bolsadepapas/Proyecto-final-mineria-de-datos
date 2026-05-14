import pandas as pd
import streamlit as st
import os

@st.cache_data
def cargar_datos():
    # Basado en tu terminal: subimos dos niveles (..) desde 'Cod' -> 'Parcial_Dashboard' -> 'final_proyect'
    # y luego entramos a 'Dataset´s'
    ruta = os.path.join('..', '..', 'Dataset´s', 'Genio3_ABrz.csv')
    
    try:
        df = pd.read_csv(ruta)
        
        # Limpieza inicial estándar
        if 'Anio' in df.columns:
            df['Anio'] = df['Anio'].astype(int)
            
        return df
        
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo en la ruta relativa: {ruta}. Asegúrate de estar ejecutando Streamlit desde la carpeta 'Cod'.")
        return pd.DataFrame()