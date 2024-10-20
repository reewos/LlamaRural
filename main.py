import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="LlamaRural - Análisis de Cobertura",
    layout="wide"
)

# Cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('resources/MOBILE_SERVICE_COVERAGE_BY_COMPANY.csv', 
                        sep=';', 
                        encoding='latin-1')
        
        # Limpieza básica de datos
        # df['LATITUD'] = df['LATITUD'].str.replace(',', '.').astype(float)
        # df['LONGITUD'] = df['LONGITUD'].str.replace(',', '.').astype(float)
        
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

# Función simplificada para encontrar estaciones cercanas
def find_nearby_stations(df, lat, lon, radius_km=5):
    try:
        # Convertir coordenadas a float y calcular distancias usando numpy
        df['distance'] = np.sqrt(
            (df['LATITUD'] - lat)**2 + 
            (df['LONGITUD'] - lon)**2
        ) * 111  # Conversión aproximada a kilómetros
        
        # Filtrar por radio
        nearby_df = df[df['distance'] <= radius_km].copy()
        
        # Convertir a lista de diccionarios
        nearby = []
        for _, row in nearby_df.iterrows():
            nearby.append({
                'distancia': round(row['distance'], 2),
                'centro_poblado': row['CENTRO_POBLADO'],
                'operador': row['EMPRESA_OPERADORA'],
                'lat': row['LATITUD'],
                'lon': row['LONGITUD'],
                'tecnologias': []  # Añadiremos después
            })

        nearby = sorted(nearby, key=lambda x: x['distancia'])  # Ordenar por distancia
        
        return nearby
    except Exception as e:
        st.error(f"Error en búsqueda: {str(e)}")
        return []

def create_simple_map(lat, lon, nearby_stations):
    try:
        m = folium.Map(location=[lat, lon], zoom_start=12)
        
        # Marcador del usuario
        folium.Marker(
            [lat, lon],
            popup="Tu ubicación",
            icon=folium.Icon(color='red')
        ).add_to(m)
        
        # Marcadores de estaciones
        for station in nearby_stations:
            folium.Marker(
                [station['lat'], station['lon']],
                popup=f"{station['centro_poblado']} - {station['distancia']}km",
                icon=folium.Icon(color='blue')
            ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error en mapa: {str(e)}")
        return None

def main():
    st.title("🌟 LlamaRural")
    st.subheader("Análisis de Cobertura en Zonas Rurales")
    
    # Cargar datos
    df = load_data()
    if df is None:
        return
    
    # Layout principal
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.subheader("📍 Ubicación")
        lat = st.number_input("Latitud", value=-12.9450053)
        lon = st.number_input("Longitud", value=-76.4200831)
        
        if st.button("Analizar Cobertura"):
            # Buscar estaciones cercanas
            nearby = find_nearby_stations(df, lat, lon)
            
            if nearby:
                st.success(f"Se encontraron {len(nearby)} estaciones cercanas")
                
                # Mostrar mapa
                st.subheader("🗺️ Mapa de Cobertura")
                m = create_simple_map(lat, lon, nearby)
                if m:
                    folium_static(m)
                
                # Mostrar estaciones encontradas
                for station in nearby:
                    st.write(f"📡 {station['centro_poblado']} - {station['operador']} - {station['distancia']}km")
            else:
                st.warning("No se encontraron estaciones en un radio de 5km")
    
    with col2:
        st.subheader("📊 Estadísticas")
        st.metric("Total Estaciones", len(df))
        st.metric("Total Operadores", df['EMPRESA_OPERADORA'].nunique())
        total_estaciones = len(df)
        st.metric("Total Estaciones", total_estaciones)
        
        tecnologias = {
            '2G': df['2G'].sum(),
            '3G': df['3G'].sum(),
            '4G': df['4G'].sum(),
            '5G': df['5G'].sum()
        }
        
        for tech, count in tecnologias.items():
            st.metric(f"Estaciones {tech}", count)
if __name__ == "__main__":
    main()