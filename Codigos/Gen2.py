import pandas as pd

def limpieza_binaria_rapida():
    # Cargamos tu dataset original
    archivo_input = 'Genio2.csv'
    df = pd.read_csv(archivo_input)
    
    print("🧹 Simplificando variables a binario...")

    # 1. Logistica_Aerea: 0 si no hay pista, 1 si hay algo
    df['Logistica_Aerea'] = df['Logistica_Aerea'].apply(
        lambda x: 0 if 'sin pista' in str(x).lower() or 'sin registro' in str(x).lower() else 1
    )

    # 2. Deforestacion_Oficial: 0 si no está registrado, 1 si dice cualquier fuente (Geobosque, etc)
    df['Deforestacion_Oficial'] = df['Deforestacion_Oficial'].apply(
        lambda x: 0 if 'no registrado' in str(x).lower() or 'sin registro' in str(x).lower() else 1
    )

    # Guardamos con el nombre que prefieras
    df.to_csv('Genio2.1.csv', index=False)
    print("✅ ¡Listo! Logistica_Aerea y Deforestacion_Oficial ahora son 0/1.")

if __name__ == "__main__":
    limpieza_binaria_rapida()