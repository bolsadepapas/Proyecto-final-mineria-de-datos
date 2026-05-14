import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# MANTENEMOS ESTA FUNCIÓN IGUAL (SE USA EN PESTAÑA 3)
def grafico_presion_pais(df):
    """Genera un gráfico de barras horizontales interactivo por país"""
    df_limpio = df[df['Pais'] != 'Sin registro']
    conteo = df_limpio['Pais'].value_counts().reset_index()
    conteo.columns = ['País', 'Cantidad de Forados']
    fig = px.bar(conteo, x='Cantidad de Forados', y='País', orientation='h',
                 title='Distribución Transfronteriza de Forados Mineros',
                 color='Cantidad de Forados', 
                 color_continuous_scale='Reds')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

# --- NUEVAS FUNCIONES DE MAPA (PESTAÑA 1) ---

# Altura estándar para que sean "grandes"
ALTURA_MAPA = 600

def mapa_fidelidad_cartografico(df):
    """Genera un mapa fidedigno grande con fondo claro y puntos rojos por área"""
    df_mapa = df[df['es_activa'] == True].copy() if 'es_activa' in df.columns else df.copy()
    
    fig = px.scatter_mapbox(df_mapa, 
                            lat="Lat", lon="Lon", 
                            hover_name="Pais", 
                            hover_data=["Area_Ha", "Validacion_Oficial", "Nivel_Confianza", "nivel_riesgo"],
                            color="Nivel_Confianza", 
                            color_continuous_scale="Reds", 
                            size="Area_Ha",
                            zoom=4,
                            mapbox_style="carto-positron", # FONDO BLANCO/CLARO
                            height=ALTURA_MAPA, # GRANDE
                            title="Mapa de Focos Mineros Activos (Fidelidad Cartográfica)")
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

def mapa_fidelidad_calor(df):
    """Genera un mapa de calor grande con fondo claro basado en área"""
    df_mapa = df[df['es_activa'] == True].copy() if 'es_activa' in df.columns else df.copy()
    
    fig = px.density_mapbox(df_mapa, 
                            lat="Lat", lon="Lon", 
                            z="Area_Ha", 
                            radius=10,
                            zoom=4,
                            mapbox_style="carto-positron", # FONDO BLANCO/CLARO
                            height=ALTURA_MAPA, # GRANDE
                            title="Mapa de Calor de Focos Mineros Activos")
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

def mapa_fidelidad_satelite(df):
    """Genera un mapa satelital fidedigno grande para visualización directa"""
    df_mapa = df[df['es_activa'] == True].copy() if 'es_activa' in df.columns else df.copy()
    
    fig = px.scatter_mapbox(df_mapa, 
                            lat="Lat", lon="Lon", 
                            hover_name="Pais", 
                            hover_data=["Area_Ha", "Validacion_Oficial", "Nivel_Confianza", "nivel_riesgo"],
                            color="Nivel_Confianza", 
                            color_continuous_scale="Reds", 
                            size="Area_Ha",
                            zoom=4,
                            mapbox_style="satellite-streets", # MAPA SATELITAL (Mejor de lo mejor)
                            height=ALTURA_MAPA, # GRANDE
                            title="Visualización Satelital de Focos Mineros Activos")
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

# MANTENEMOS ESTA FUNCIÓN IGUAL (SE USA EN PESTAÑA 1, PERO SE REACOMODARÁ)
# Es la misma que grafico_presion_pais, pero con un nombre diferente para mayor claridad en app.py
def grafico_barras_transfronterizo(df):
    return grafico_presion_pais(df)

# --- MANTENEMOS EL RESTO DE FUNCIONES IGUAL (PESTAÑAS 2 Y 3) ---

def grafico_dispersion_logistica(df, pais_seleccionado="Todos"):
    """Compara la cercanía vs la densidad, coloreado por logística aérea"""
    df_plot = df if pais_seleccionado == "Todos" else df[df['Pais'] == pais_seleccionado]
    df_plot['Logística'] = df_plot['Logistica_Aerea'].map({1: 'Con Pista Aérea', 0: 'Sin Pista'})
    fig = px.scatter(df_plot, 
                     x='dist_vecino_km', y='densidad_10km', 
                     color='Logística',
                     color_discrete_map={'Con Pista Aérea': 'red', 'Sin Pista': 'blue'},
                     opacity=0.6,
                     title=f'Densidad vs Aislamiento ({pais_seleccionado})',
                     labels={'dist_vecino_km': 'Distancia al vecino más cercano (km)',
                             'densidad_10km': 'Cantidad de vecinos en 10km (Densidad)'})
    fig.update_xaxes(autorange="reversed")
    return fig

def grafico_boxplot_logistica(df, pais_seleccionado="Todos"):
    """Compara estadísticamente si tener pista aumenta la densidad de forados"""
    df_plot = df if pais_seleccionado == "Todos" else df[df['Pais'] == pais_seleccionado]
    df_plot['Logística'] = df_plot['Logistica_Aerea'].map({1: 'Con Pista Aérea', 0: 'Sin Pista'})
    fig = px.box(df_plot, 
                 x='Logística', y='densidad_10km', 
                 color='Logística',
                 color_discrete_map={'Con Pista Aérea': 'red', 'Sin Pista': 'blue'},
                 title='Impacto de Pistas Aéreas en la Creación de Clústeres')
    return fig

def grafico_tendencia_crecimiento(df):
    """Muestra la tendencia del área total deforestada por año"""
    df_year = df.groupby('Anio')['Area_Ha'].sum().reset_index()
    fig = px.line(df_year, x='Anio', y='Area_Ha', markers=True,
                  title='Evolución del Área Total Afectada',
                  labels={'Area_Ha': 'Hectáreas Totales', 'Anio': 'Año'},
                  line_shape='spline', 
                  color_discrete_sequence=['#d62728'])
    return fig

def grafico_persistencia(df):
    """Histograma para ver cuántos años sobreviven los forados"""
    fig = px.histogram(df, x='indice_persistencia', nbins=10,
                       title='Supervivencia de Clústeres (Persistencia)',
                       labels={'indice_persistencia': 'Años de Actividad Continua'},
                       color_discrete_sequence=['teal'])
    fig.update_yaxes(title_text="Cantidad de Forados")
    return fig

def grafico_oro_vs_mineria(df):
    """Gráfico de doble eje: Precio del oro (línea) vs Forados activos (barras)"""
    df_year = df.groupby('Anio').agg({'precio_oro': 'mean', 'Anio': 'count'}).rename(columns={'Anio': 'Cantidad_Forados'}).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=df_year['Anio'], y=df_year['Cantidad_Forados'], name="Forados Activos", opacity=0.7, marker_color='darkorange'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df_year['Anio'], y=df_year['precio_oro'], name="Precio del Oro (USD)", mode='lines+markers', line=dict(color='gold', width=4)),
        secondary_y=True,
    )
    fig.update_layout(title_text="Correlación: Precio del Oro vs Expansión Minera")
    fig.update_xaxes(title_text="Año")
    fig.update_yaxes(title_text="Cantidad de Forados", secondary_y=False)
    fig.update_yaxes(title_text="Precio del Oro (USD)", secondary_y=True)
    return fig