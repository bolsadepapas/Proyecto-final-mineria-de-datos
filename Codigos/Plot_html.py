import pandas as pd
import json
import os

# Construir ruta relativa correcta desde la carpeta Codigos
archivo_input = os.path.join(os.path.dirname(__file__), '..', 'Dataset´s', 'Genio3.csv')

print(f"Intentando cargar: {archivo_input}")
print(f"Ruta absoluta: {os.path.abspath(archivo_input)}\n")

try:
    df = pd.read_csv(archivo_input)
    print(f"✅ Archivo cargado exitosamente. Forma: {df.shape}")
    print(f"\nColumnas encontradas:")
    print(df.columns.tolist())
    print(f"\nPrimeros registros:")
    print(df.head(2))
    print()
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo {archivo_input}")
    print(f"Directorio actual: {os.getcwd()}")
    exit()

# Convertir DataFrame a JSON (formato compatible con D3.js)
datos_json = df.to_json(orient='records')

# Crear HTML con datos embebidos
html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Genio3: Dashboard de Inteligencia Ambiental</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
    
    <style>
        :root {{ --dark: #1a1a1a; --gold: #ffd700; --danger: #ff4d4d; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #ececec; margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 15px; }}
        header {{ grid-column: 1 / -1; background: var(--dark); color: white; padding: 15px; border-radius: 8px; text-align: center; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .full-width {{ grid-column: 1 / -1; }}
        #map {{ height: 500px; width: 100%; border-radius: 8px; }}
        h2 {{ margin-top: 0; color: #444; font-size: 1.2rem; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; font-weight: bold; }}
        .status.loading {{ background: #fff3cd; color: #856404; }}
        .status.success {{ background: #d4edda; color: #155724; }}
        .status.error {{ background: #f8d7da; color: #721c24; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px; }}
        .stat-box {{ background: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center; }}
        .stat-box h3 {{ margin: 0; color: #666; font-size: 0.9rem; }}
        .stat-box p {{ margin: 5px 0 0 0; font-size: 1.5rem; font-weight: bold; color: #333; }}
    </style>
</head>
<body>

    <header>
        <h1>PROYECTO GENIO 3: Monitoreo Satelital de Minería Ilegal</h1>
        <p>Análisis Multidimensional de la Amazonía Transfronteriza</p>
    </header>

    <div class="card full-width">
        <div id="status" class="status success">✅ Dashboard cargado correctamente</div>
        <div class="stats">
            <div class="stat-box">
                <h3>Total de Registros</h3>
                <p id="stat-registros">0</p>
            </div>
            <div class="stat-box">
                <h3>Países</h3>
                <p id="stat-paises">0</p>
            </div>
            <div class="stat-box">
                <h3>Hectáreas Totales</h3>
                <p id="stat-hectareas">0</p>
            </div>
            <div class="stat-box">
                <h3>Persistencia Promedio</h3>
                <p id="stat-persistencia">0</p>
            </div>
        </div>
    </div>

    <div class="card full-width">
        <h2>📍 Hotspots y Fronteras (Vista Satelital)</h2>
        <div id="map"></div>
    </div>

    <div class="card">
        <h2>📈 Hipótesis 1: Oro vs. Deforestación</h2>
        <canvas id="mixedChart"></canvas>
    </div>

    <div class="card">
        <h2>🛡️ Hipótesis 3: Persistencia por Nivel de Riesgo</h2>
        <canvas id="radarChart"></canvas>
    </div>

    <script>
        // DATOS EMBEBIDOS EN EL HTML (Sin necesidad de cargar CSV)
        const data = {datos_json};

        console.log('✅ Datos embebidos cargados. Total de registros:', data.length);
        if (data.length > 0) {{
            console.log('Primeras columnas:', Object.keys(data[0]));
        }}

        // Calcular estadísticas
        const totalRegistros = data.length;
        const paises = [...new Set(data.map(d => d.Pais))].length;
        const hectareasTotal = data.reduce((sum, d) => sum + (parseFloat(d.Area_Ha) || 0), 0);
        const persistenciaPromedio = (data.reduce((sum, d) => sum + (parseFloat(d.indice_persistencia) || 0), 0) / totalRegistros).toFixed(2);

        document.getElementById('stat-registros').textContent = totalRegistros.toLocaleString('es-ES');
        document.getElementById('stat-paises').textContent = paises;
        document.getElementById('stat-hectareas').textContent = hectareasTotal.toLocaleString('es-ES', {{maximumFractionDigits: 0}});
        document.getElementById('stat-persistencia').textContent = persistenciaPromedio;

        console.log('Estadísticas calculadas:', {{
            totalRegistros,
            paises,
            hectareasTotal: hectareasTotal.toFixed(0),
            persistenciaPromedio
        }});

        const años = [...new Set(data.map(d => String(d.Anio)))].sort();
        console.log('Años encontrados:', años);
        
        // --- 1. MAPA PROFESIONAL ---
        const map = L.map('map').setView([-11.0, -68.0], 5); 
        const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
        
        // Mapa de calor con validación estricta
        const heatPoints = data
            .filter(d => {{
                const lat = parseFloat(d.Lat);
                const lon = parseFloat(d.Lon);
                return !isNaN(lat) && !isNaN(lon) && lat !== 0 && lon !== 0;
            }})
            .map(d => [parseFloat(d.Lat), parseFloat(d.Lon), 0.8]);
        
        console.log('Puntos del mapa de calor válidos:', heatPoints.length);
        
        if (heatPoints.length > 0) {{
            L.heatLayer(heatPoints, {{radius: 18, blur: 15, gradient: {{0.4: 'blue', 0.65: 'lime', 1: 'red'}}}}).addTo(map);
            console.log('✅ Mapa de calor creado con', heatPoints.length, 'puntos');
        }} else {{
            console.warn('⚠️ No hay puntos válidos para el mapa de calor');
        }}

        // --- 2. GRÁFICO MIXTO: ORO Y ÁREA ---
        const areas = años.map(a => {{
            const suma = data
                .filter(d => String(d.Anio) === a)
                .reduce((sum, d) => sum + (parseFloat(d.Area_Ha) || 0), 0);
            return suma;
        }});
        
        const precios = años.map(a => {{
            const valores = data
                .filter(d => String(d.Anio) === a)
                .map(d => parseFloat(d.precio_oro))
                .filter(v => !isNaN(v));
            return valores.length > 0 ? valores.reduce((a, b) => a + b, 0) / valores.length : 0;
        }});

        console.log('Datos para gráfico mixto - Áreas:', areas, 'Precios:', precios);

        new Chart(document.getElementById('mixedChart'), {{
            type: 'bar',
            data: {{
                labels: años,
                datasets: [
                    {{ 
                        label: 'Hectáreas (Suma)', 
                        data: areas, 
                        backgroundColor: '#2e7d32', 
                        yAxisID: 'y',
                        borderRadius: 5
                    }},
                    {{ 
                        label: 'Precio Oro (Promedio USD/oz)', 
                        data: precios, 
                        type: 'line', 
                        borderColor: '#f9a825', 
                        backgroundColor: 'rgba(249, 168, 37, 0.1)',
                        borderWidth: 3, 
                        yAxisID: 'y1',
                        tension: 0.4
                    }}
                ]
            }},
            options: {{ 
                responsive: true,
                interaction: {{ mode: 'index', intersect: false }},
                scales: {{ 
                    y: {{ 
                        position: 'left', 
                        title: {{ display: true, text: 'Hectáreas (Ha)' }},
                        beginAtZero: true
                    }}, 
                    y1: {{ 
                        position: 'right', 
                        title: {{ display: true, text: 'Precio USD/oz' }},
                        beginAtZero: true,
                        grid: {{ drawOnChartArea: false }}
                    }} 
                }}
            }}
        }});

        console.log('✅ Gráfico mixto creado');

        // --- 3. GRÁFICO DE RADAR: RIESGO ---
        const riesgos = ['BAJO', 'MODERADO', 'ALTO', 'CRÍTICO'];
        const persistenciaPromedioPorRiesgo = riesgos.map(r => {{
            const subset = data.filter(d => d.nivel_riesgo === r);
            if (subset.length === 0) return 0;
            const valores = subset.map(d => parseFloat(d.indice_persistencia)).filter(v => !isNaN(v));
            const promedio = valores.length > 0 ? valores.reduce((a, b) => a + b, 0) / valores.length : 0;
            console.log(`Riesgo ${{r}}: ${{subset.length}} registros, persistencia promedio: ${{promedio.toFixed(2)}}`);
            return promedio;
        }});

        new Chart(document.getElementById('radarChart'), {{
            type: 'radar',
            data: {{
                labels: riesgos,
                datasets: [{{
                    label: 'Años de Persistencia Media',
                    data: persistenciaPromedioPorRiesgo,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgb(255, 99, 132)',
                    pointBackgroundColor: 'rgb(255, 99, 132)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }}]
            }},
            options: {{ 
                responsive: true,
                elements: {{ line: {{ borderWidth: 3 }} }},
                scales: {{
                    r: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Años' }}
                    }}
                }}
            }}
        }});

        console.log('✅ Todos los gráficos creados correctamente');
    </script>
</body>
</html>"""

# Guardar HTML
archivo_output = os.path.join(os.path.dirname(__file__), '..', 'Visualizer', 'dashboard_genio3_embebido.html')

try:
    os.makedirs(os.path.dirname(archivo_output), exist_ok=True)
    with open(archivo_output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard HTML creado exitosamente")
    print(f"✅ Ubicación: {archivo_output}")
    print(f"✅ Tamaño del archivo: {len(html_content)} caracteres")
    print(f"\n📊 Datos embebidos en el HTML:")
    print(f"   • Total de registros: {len(df)}")
    print(f"   • Países únicos: {df['Pais'].nunique()}")
    print(f"   • Años: {sorted(df['Anio'].unique())}")
    print(f"   • Hectáreas totales: {df['Area_Ha'].sum():.0f}")
    print(f"   • Persistencia promedio: {df['indice_persistencia'].mean():.2f} años")
    print(f"   • Niveles de riesgo: {df['nivel_riesgo'].unique().tolist()}")
    print(f"\n✨ El dashboard está completamente funcional sin necesidad de cargar CSV")
    
except Exception as e:
    print(f"❌ Error al guardar HTML: {e}")
    exit()