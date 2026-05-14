import streamlit as st
import data_manager as dm
import visualizaciones as vis
import pandas as pd

# 1. Configuración de la página (Debe ser la primera línea de Streamlit)
st.set_page_config(page_title="Análisis Espacial - Minería", layout="wide")

# 2. Cargar los datos usando nuestro módulo
df = dm.cargar_datos()

if df.empty:
    st.stop() # Detiene la ejecución si no hay datos

# 3. Diseño del Menú Lateral (Sidebar)
st.sidebar.title("Navegación")
st.sidebar.markdown("Dashboard interactivo para la validación de hipótesis sobre la expansión de clústeres mineros informales.")

menu = st.sidebar.radio(
    "Seleccione el módulo de análisis:",
    [
        "1. Visión General y Presión Territorial",
        "2. Motores de Clústeres y Logística",
        "3. Tendencias y Persistencia"
    ]
)

st.sidebar.markdown("---")
st.sidebar.success(f"Conexión exitosa: {len(df)} registros cargados.")

# 4. Estructura de las Pestañas (Lógica de ruteo)
st.title("Dashboard de Inteligencia Espacial - Genio3")

if menu == "1. Visión General y Presión Territorial":
    st.header("Visión General y Presión Territorial")
    st.markdown("**(Contexto)**: ¿Qué porcentaje de forados hay en zonas protegidas y cómo se distribuyen?")
    
    # --- 1. CÁLCULO DE KPIs ---
    total_forados = len(df)
    area_total = df['Area_Ha'].sum()
    
    # Calculamos % en áreas protegidas
    # Aseguramos que 'Area_Protegida' exista y no sea nulo
    if 'Area_Protegida' in df.columns:
        df_protegido = df[(df['Area_Protegida'] != 'Sin registro') & (df['Area_Protegida'].notna())]
        porcentaje_protegido = (len(df_protegido) / total_forados) * 100
    else:
        porcentaje_protegido = 0
    
    # --- 2. MOSTRAR TARJETAS (Métricas) ---
    st.markdown("### Métricas Clave de Impacto")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Forados Detectados", f"{total_forados:,}")
    with col2:
        st.metric("Hectáreas Deforestadas Acum.", f"{area_total:,.2f} Ha")
    with col3:
        st.metric("Forados en Zonas Protegidas", f"{porcentaje_protegido:.1f}%", "Alerta Crítica", delta_color="inverse")
        
    st.markdown("---")
    
    # --- 3. SELECTOR DE VISTA DE MAPA Y MAPA GRANDE ---
    st.markdown("#### Distribución Espacial (Mapa Grande e Interactivo)")
    # Selector de radio en la página principal para mayor visibilidad
    map_mode = st.radio(
        "Seleccione tipo de vista de mapa (Fondo Claro/Blanco):",
        ["Cartográfico (Fidelidad)", "Mapa de Calor", "Satelital (Mejor de lo mejor)"],
        horizontal=True
    )
    
    # Renderizar el mapa grande basado en la selección
    if map_mode == "Cartográfico (Fidelidad)":
        fig_mapa = vis.mapa_fidelidad_cartografico(df)
    elif map_mode == "Mapa de Calor":
        fig_mapa = vis.mapa_fidelidad_calor(df)
    elif map_mode == "Satelital (Mejor de lo mejor)":
        fig_mapa = vis.mapa_fidelidad_satelite(df)
    
    # Mostrar el mapa ocupando todo el ancho
    st.plotly_chart(fig_mapa, use_container_width=True)
    
    st.markdown("---")
    
    # --- 4. GRÁFICO DE BARRAS ABAJO ---
    st.markdown("#### Análisis Transfronterizo (Gráfico Estadístico)")
    fig_barras = vis.grafico_barras_transfronterizo(df)
    st.plotly_chart(fig_barras, use_container_width=True)

# MANTENEMOS EL RESTO DE PESTAÑAS IGUAL (CORRIENDO LOCALMENTE)

elif menu == "2. Motores de Clústeres y Logística":
    st.header("Motores de Clústeres y Logística")
    st.markdown("**(Comportamiento)**: ¿La implementación de pistas hace que los forados mineros formen clústeres más densos en selva profunda?")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filtros de Análisis")
    if 'Pais' in df.columns:
        lista_paises = ["Todos"] + list(df[df['Pais'] != 'Sin registro']['Pais'].unique())
        pais_seleccionado = st.sidebar.selectbox("Seleccione un País (Ej. Guyana):", lista_paises)
    else:
        pais_seleccionado = "Todos"
    
    df_filtro = df if pais_seleccionado == "Todos" else df[df['Pais'] == pais_seleccionado]
    
    if len(df_filtro) > 0 and 'Logistica_Aerea' in df.columns and 'densidad_10km' in df.columns:
        densidad_con_pista = df_filtro[df_filtro['Logistica_Aerea'] == 1]['densidad_10km'].mean()
        densidad_sin_pista = df_filtro[df_filtro['Logistica_Aerea'] == 0]['densidad_10km'].mean()
        
        st.markdown(f"### Análisis de Comportamiento para: **{pais_seleccionado}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Densidad Promedio (Sin Pistas)", value=f"{densidad_sin_pista:.1f} vecinos")
        with col2:
            st.metric(label="Densidad Promedio (Con Pistas)", value=f"{densidad_con_pista:.1f} vecinos", delta="Alta Concentración", delta_color="inverse")
            
        st.info("💡 **Interpretación**: Si la métrica de 'Con Pistas' es mayor, se comprueba tu hipótesis: la logística aérea actúa como un imán para nuevos forados, facilitando la extracción del mineral en selva profunda.")
        
        st.markdown("---")
        col_izq, col_der = st.columns([1, 1])
        
        with col_izq:
            fig_scatter = vis.grafico_dispersion_logistica(df, pais_seleccionado)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_der:
            fig_box = vis.grafico_boxplot_logistica(df, pais_seleccionado)
            st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No hay datos suficientes o faltan columnas clave para este país.")

elif menu == "3. Tendencias y Persistencia":
    st.header("Tendencias de Crecimiento y Persistencia")
    st.markdown("**(Evolución temporal)**: ¿Qué tanto tienden a crecer en el tiempo los forados? ¿Están impulsados por el mercado global?")
    
    if 'crecimiento_ha' in df.columns:
        crecimiento_promedio = df[df['crecimiento_ha'] > 0]['crecimiento_ha'].mean()
        
        st.markdown("### Tasa de Expansión")
        st.metric(label="Crecimiento Promedio Interanual", 
                  value=f"{crecimiento_promedio:.2f} Ha", 
                  delta="Por cada forado activo al año", 
                  delta_color="inverse")
    
    st.markdown("---")
    
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        fig_tendencia = vis.grafico_tendencia_crecimiento(df)
        st.plotly_chart(fig_tendencia, use_container_width=True)
        
    with col_der:
        fig_persistencia = vis.grafico_persistencia(df)
        st.plotly_chart(fig_persistencia, use_container_width=True)
        st.info("💡 **Interpretación**: Si la persistencia es alta (barras grandes hacia la derecha), significa que los mineros operan durante años sin intervención estatal.")
        
    st.markdown("---")
    
    st.markdown("### Factor Económico: El Motor de la Fiebre del Oro")
    if 'precio_oro' in df.columns:
        fig_oro = vis.grafico_oro_vs_mineria(df)
        st.plotly_chart(fig_oro, use_container_width=True)
        st.success("💡 **Hipótesis Comprobada**: Si la curva amarilla (oro) sube a la par que las barras naranjas (forados), demostramos estadísticamente que la minería informal responde directamente a los incentivos del mercado internacional.")
    else:
        st.warning("No hay datos suficientes para el análisis del precio del oro.")