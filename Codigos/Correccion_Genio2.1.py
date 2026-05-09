import pandas as pd
import os

# Construir ruta relativa correcta desde la carpeta Codigos
archivo_input = os.path.join(os.path.dirname(__file__), '..', 'Dataset´s', 'Genio2.1.csv')

print(f"Intentando cargar: {archivo_input}")
print(f"Ruta absoluta: {os.path.abspath(archivo_input)}\n")

try:
    df = pd.read_csv(archivo_input)
    print(f"✅ Archivo cargado exitosamente. Forma: {df.shape}\n")
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo {archivo_input}")
    print(f"Directorio actual: {os.getcwd()}")
    exit()

def recalcular_riesgo(row):
    """Calcula el nivel de riesgo basado en múltiples criterios"""
    # CRÍTICO: Si hay área protegida
    if str(row['Area_Protegida']).lower() != 'sin registro':
        return 'CRÍTICO'
    # ALTO: Si hay comunidad indígena O el área es mayor a 50 hectáreas
    elif str(row['Comunidad_Indigena']).lower() != 'sin registro' or row['Area_Ha'] > 50:
        return 'ALTO'
    # MODERADO: Si hay muchas minas cerca (Efecto Colmena alto)
    elif row['densidad_10km'] > 5:
        return 'MODERADO'
    # BAJO: Minas aisladas en zonas no protegidas
    else:
        return 'BAJO'

print("Recalculando niveles de riesgo...")
df['nivel_riesgo'] = df.apply(recalcular_riesgo, axis=1)

# Guardar archivo corregido
archivo_output = os.path.join(os.path.dirname(__file__), '..', 'Dataset´s', 'Genio2.1_Corregido.csv')

try:
    df.to_csv(archivo_output, index=False)
    print(f"✅ Riesgo recalculado. Ahora los datos tienen variedad.")
    print(f"✅ Archivo guardado en: {archivo_output}\n")
    
    # Mostrar resumen de riesgos
    print("Distribución de niveles de riesgo:")
    print(df['nivel_riesgo'].value_counts().sort_index())
except Exception as e:
    print(f"❌ Error al guardar el archivo: {e}")