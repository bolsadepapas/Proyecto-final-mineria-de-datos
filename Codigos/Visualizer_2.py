import pandas as pd
import json
import os

# Ruta al dataset
archivo_input = os.path.join(os.path.dirname(__file__), '..', 'Dataset´s', 'Genio3.csv')

try:
    df = pd.read_csv(archivo_input)
    print(f"Total de registros antes de limpieza: {len(df)}")
    
    # CRÍTICO: Eliminar registros con "Sin registro" en columnas clave
    df = df[
        (df['Area_Protegida'].astype(str).str.strip().str.lower() != 'sin registro') |
        (df['Comunidad_Indigena'].astype(str).str.strip().str.lower() != 'sin registro')
    ]
    
    print(f"Total de registros después de eliminar 'Sin registro': {len(df)}")
    
    # Limpieza de datos críticos
    df['Logistica_Aerea'] = df['Logistica_Aerea'].astype(str)
    df['Pais'] = df['Pais'].fillna('Desconocido')
    
    # Asegurar tipos de datos numéricos
    df['densidad_10km'] = pd.to_numeric(df['densidad_10km'], errors='coerce')
    df['dist_vecino_km'] = pd.to_numeric(df['dist_vecino_km'], errors='coerce')
    df['Area_Ha'] = pd.to_numeric(df['Area_Ha'], errors='coerce')
    df['indice_persistencia'] = pd.to_numeric(df['indice_persistencia'], errors='coerce')
    
    datos_json = df.to_json(orient='records')
    
    # Obtener países de los datos limpios
    paises_lista = sorted(df['Pais'].unique().tolist())
    
    print(f"✅ Datos cargados y procesados exitosamente")
    print(f"✅ Países encontrados: {paises_lista}")
    
except Exception as e:
    print(f"❌ Error al cargar datos: {e}")
    exit()

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Análisis Avanzado Genio3 - UNSA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        header {{ grid-column: 1 / -1; background: #1a2a3a; color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .full-width {{ grid-column: 1 / -1; }}
        #map {{ height: 450px; width: 100%; border-radius: 8px; }}
        h2 {{ color: #2c3e50; font-size: 1.1rem; border-bottom: 2px solid #3498db; padding-bottom: 8px; margin-top: 0; }}
        .desc {{ font-size: 0.85rem; color: #666; margin: 10px 0; line-height: 1.4; }}
        .chart-container {{ position: relative; height: 300px; }}
        
        /* Estilos para los toggles de países */
        .country-toggles {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; padding: 10px; background: #f9f9f9; border-radius: 8px; }}
        .country-toggle {{ 
            padding: 8px 12px; 
            border: 2px solid #ddd; 
            border-radius: 20px; 
            background: white;
            cursor: pointer; 
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        .country-toggle:hover {{ border-color: #3498db; }}
        .country-toggle.active {{ 
            background: #3498db; 
            color: white; 
            border-color: #3498db;
        }}
        
        /* Clase para desactivados */
        .country-toggle.inactive {{ 
            opacity: 0.5;
            background: #eee;
        }}
    </style>
</head>
<body>

<header>
    <h1>Dashboard Genio3: Inteligencia de Datos Espaciales</h1>
    <p>Análisis de Patrones de Deforestación en la Amazonía Transfronteriza</p>
    <p style="font-size: 0.9rem; margin: 10px 0 0 0;">⚠️ Nota: Se han eliminado registros con "Sin registro" en Áreas Protegidas o Comunidades Indígenas</p>
</header>

<div class="card full-width">
    <h2>📍 Mapa de Calor: Concentración de Impacto</h2>
    <p class="desc">Localización de Hotspots detectados. Las zonas rojas indican saturación de actividad minera ilegal.</p>
    <div id="map"></div>
</div>

<div class="card">
    <h2>📊 H1: Eficiencia Logística por País</h2>
    <p class="desc">Comparación del área promedio deforestada según la presencia de pistas de aterrizaje.</p>
    <div class="chart-container">
        <canvas id="chartLogistica"></canvas>
    </div>
</div>

<div class="card">
    <h2>📈 H2: Análisis de Saturación (Colmena) - Interactivo</h2>
    <p class="desc">Relación inversa entre densidad de focos y distancia al vecino. Indica colapso del territorio. Haz clic en los países para mostrar/ocultar.</p>
    <div class="country-toggles" id="countryToggles"></div>
    <div class="chart-container">
        <canvas id="chartColmena"></canvas>
    </div>
</div>

<div class="card">
    <h2>🛡️ H3: Perfiles de Persistencia Geopolítica</h2>
    <p class="desc">Área vs. Años de persistencia. El tamaño de la burbuja indica el volumen de detecciones.</p>
    <div class="chart-container">
        <canvas id="chartBurbujas"></canvas>
    </div>
</div>

<div class="card">
    <h2>⚠️ H4: Distribución de Riesgo por Territorio</h2>
    <p class="desc">Análisis de vulnerabilidad: ¿Cuántos focos caen en categorías Críticas por cada país?</p>
    <div class="chart-container">
        <canvas id="chartRiesgo"></canvas>
    </div>
</div>

<script>
    const data = {datos_json};
    const paises = {json.dumps(paises_lista)};
    const colores = {{'Peru': '#3498db', 'Brasil': '#e74c3c', 'Bolivia': '#2ecc71', 'Colombia': '#f1c40f', 'Ecuador': '#9b59b6', 'Venezuela': '#e67e22'}};
    
    console.log('Total de registros después de limpieza:', data.length);
    console.log('Países encontrados:', paises);

    // --- 1. MAPA ---
    const map = L.map('map').setView([-11.0, -68.0], 5);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
    const heatPoints = data
        .filter(d => !isNaN(parseFloat(d.Lat)) && !isNaN(parseFloat(d.Lon)))
        .map(d => [parseFloat(d.Lat), parseFloat(d.Lon), 0.7]);
    L.heatLayer(heatPoints, {{radius: 15, blur: 20}}).addTo(map);
    console.log('Mapa cargado con', heatPoints.length, 'puntos');

    // --- 2. H1: LOGÍSTICA POR PAÍS ---
    new Chart(document.getElementById('chartLogistica'), {{
        type: 'bar',
        data: {{
            labels: paises,
            datasets: [
                {{
                    label: 'Sin Pista',
                    data: paises.map(p => {{
                        const vals = data.filter(d => d.Pais === p && d.Logistica_Aerea == "0").map(d => parseFloat(d.Area_Ha)).filter(v => !isNaN(v));
                        return vals.length > 0 ? vals.reduce((a, b) => a + b) / vals.length : 0;
                    }}),
                    backgroundColor: '#bdc3c7'
                }},
                {{
                    label: 'Con Pista',
                    data: paises.map(p => {{
                        const vals = data.filter(d => d.Pais === p && d.Logistica_Aerea == "1").map(d => parseFloat(d.Area_Ha)).filter(v => !isNaN(v));
                        return vals.length > 0 ? vals.reduce((a, b) => a + b) / vals.length : 0;
                    }}),
                    backgroundColor: '#e74c3c'
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                y: {{ beginAtZero: true, title: {{ display: true, text: 'Área Promedio (Ha)' }} }}
            }}
        }}
    }});

    // --- 3. H2: COLMENA (Líneas interactivas) ---
    let chartColmenaInstance = null;
    const paisesActivos = new Set(paises);

    function actualizarGraficoColmena() {{
        if (chartColmenaInstance) {{
            chartColmenaInstance.destroy();
        }}

        const datasets = paises
            .filter(p => paisesActivos.has(p))
            .map((p, i) => {{
                const puntos = data
                    .filter(d => d.Pais === p)
                    .map(d => ({{
                        x: parseFloat(d.densidad_10km) || 0,
                        y: parseFloat(d.dist_vecino_km) || 0
                    }}))
                    .sort((a, b) => a.x - b.x);

                return {{
                    label: p,
                    data: puntos,
                    borderColor: colores[p] || '#' + Math.floor(Math.random()*16777215).toString(16),
                    backgroundColor: colores[p] + '22' || '#00000022',
                    borderWidth: 2.5,
                    fill: false,
                    pointRadius: 3,
                    pointBackgroundColor: colores[p] || '#3498db',
                    tension: 0.4,
                    pointHoverRadius: 6
                }};
            }});

        chartColmenaInstance = new Chart(document.getElementById('chartColmena'), {{
            type: 'line',
            data: {{ datasets: datasets }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ mode: 'nearest', intersect: false }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Densidad de Focos (10km)' }},
                        type: 'linear',
                        position: 'bottom'
                    }},
                    y: {{
                        title: {{ display: true, text: 'Distancia al Vecino (km)' }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: true, position: 'top' }}
                }}
            }}
        }});
    }}

    // Crear toggles de países
    const toggleContainer = document.getElementById('countryToggles');
    paises.forEach(p => {{
        const btn = document.createElement('button');
        btn.textContent = p;
        btn.className = 'country-toggle active';
        btn.onclick = () => {{
            if (paisesActivos.has(p)) {{
                paisesActivos.delete(p);
                btn.classList.remove('active');
                btn.classList.add('inactive');
            }} else {{
                paisesActivos.add(p);
                btn.classList.add('active');
                btn.classList.remove('inactive');
            }}
            actualizarGraficoColmena();
        }};
        toggleContainer.appendChild(btn);
    }});

    actualizarGraficoColmena();

    // --- 4. H3: BUBBLES (Perfil) ---
    new Chart(document.getElementById('chartBurbujas'), {{
        type: 'bubble',
        data: {{
            datasets: paises.map((p, i) => {{
                const subset = data.filter(d => d.Pais === p);
                const areaPromedio = subset.map(d => parseFloat(d.Area_Ha)).filter(v => !isNaN(v));
                const persistenciaPromedio = subset.map(d => parseFloat(d.indice_persistencia)).filter(v => !isNaN(v));
                
                return {{
                    label: p,
                    data: [{{
                        x: areaPromedio.length > 0 ? areaPromedio.reduce((a, b) => a + b) / areaPromedio.length : 0,
                        y: persistenciaPromedio.length > 0 ? persistenciaPromedio.reduce((a, b) => a + b) / persistenciaPromedio.length : 0,
                        r: subset.length / 20
                    }}],
                    backgroundColor: (colores[p] || '#3498db') + '88'
                }};
            }})
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                x: {{
                    title: {{ display: true, text: 'Área Media (Ha)' }},
                    beginAtZero: true
                }},
                y: {{
                    title: {{ display: true, text: 'Persistencia Promedio (Años)' }},
                    beginAtZero: true
                }}
            }}
        }}
    }});

    // --- 5. H4: RIESGO STACKED ---
    const niveles = ['BAJO', 'MODERADO', 'ALTO', 'CRÍTICO'];
    new Chart(document.getElementById('chartRiesgo'), {{
        type: 'bar',
        data: {{
            labels: paises,
            datasets: niveles.map((n, i) => {{
                const coloresRiesgo = ['#95a5a6', '#f1c40f', '#e67e22', '#c0392b'];
                return {{
                    label: n,
                    data: paises.map(p => data.filter(d => d.Pais === p && d.nivel_riesgo === n).length),
                    backgroundColor: coloresRiesgo[i]
                }};
            }})
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                x: {{ stacked: true }},
                y: {{ stacked: true, title: {{ display: true, text: 'Cantidad de Focos' }} }}
            }}
        }}
    }});

    console.log('✅ Todos los gráficos inicializados correctamente');
</script>
</body>
</html>"""

# Guardado del archivo
output_path = os.path.join(os.path.dirname(__file__), '..', 'Visualizer', 'informe_final_genio3.html')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Dashboard completo generado en: {output_path}")
print(f"✅ Registros después de limpieza: {len(df)}")
print(f"✅ Países incluidos: {', '.join(paises_lista)}")