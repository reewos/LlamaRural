import streamlit as st
import pandas as pd
import folium
import json
from streamlit_folium import folium_static
import numpy as np
import plotly.express as px
from folium.plugins import HeatMap, MarkerCluster, Search
from branca.colormap import LinearColormap

# Configuración de la página

st.set_page_config(
    page_title="LlamaRural - Análisis de Cobertura",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'nearby_stations' not in st.session_state:
    st.session_state.nearby_stations = None

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('resources/MOBILE_SERVICE_COVERAGE_BY_COMPANY.csv', 
                        sep=';', 
                        encoding='latin-1')
        
        # Calcular tecnologías disponibles
        df['tecnologias'] = df.apply(lambda x: [tech for tech, val in 
            zip(['2G', '3G', '4G', '5G'], [x['2G'], x['3G'], x['4G'], x['5G']]) 
            if val == 'SI'], axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

# Función mejorada para encontrar estaciones cercanas
def find_nearby_stations(df, lat, lon, radius_km=5, operador_filter=None):
    try:
        # Calcular distancias usando numpy
        df['distance'] = np.sqrt(
            (df['LATITUD'] - lat)**2 + 
            (df['LONGITUD'] - lon)**2
        ) * 111  # Conversión aproximada a kilómetros
        
        # Aplicar filtros
        mask = df['distance'] <= radius_km
        if operador_filter:
            mask &= df['EMPRESA_OPERADORA'] == operador_filter
            
        nearby_df = df[mask].copy()
        
        # Convertir a lista de diccionarios
        nearby = []
        for _, row in nearby_df.iterrows():
            techs = [tech for tech, val in 
                    zip(['2G', '3G', '4G', '5G'], 
                        [row['2G'], row['3G'], row['4G'], row['5G']]) 
                    if val == 1]
            
            nearby.append({
                'distancia': round(row['distance'], 2),
                'centro_poblado': row['CENTRO_POBLADO'],
                'operador': row['EMPRESA_OPERADORA'],
                'departamento': row['DEPARTAMENTO'],
                'provincia': row['PROVINCIA'],
                'distrito': row['DISTRITO'],
                'lat': row['LATITUD'],
                'lon': row['LONGITUD'],
                'tecnologias': techs,
                'velocidad': 'Más de 1Mbps' if row['MÁS_DE_1_MBPS'] == 'SI' else 'Hasta 1Mbps'
            })
        
        return nearby
    except Exception as e:
        st.error(f"Error en búsqueda: {str(e)}")
        return []

def create_enhanced_map(lat, lon, nearby_stations):
    try:
        m = folium.Map(location=[lat, lon], zoom_start=12)
        
        # Crear grupos de marcadores por operador
        operator_groups = {}
        
        # Colores por operador
        operator_colors = {
            'TELEFÓNICA DEL PERÚ S.A.A.': 'blue',
            'AMÉRICA MÓVIL PERÚ S.A.C.': 'red',
            'VIETTEL PERÚ S.A.C.': 'green',
            'ENTEL PERÚ S.A.': 'purple'
        }
        
        # Marcador del usuario
        folium.Marker(
            [lat, lon],
            popup="Tu ubicación",
            icon=folium.Icon(color='black', icon='home')
        ).add_to(m)
        
        # Crear clusters por operador
        for station in nearby_stations:
            operator = station['operador']
            if operator not in operator_groups:
                operator_groups[operator] = MarkerCluster(name=operator)
                operator_groups[operator].add_to(m)
            
            # Crear popup con información detallada
            popup_html = f"""
                <div style='width:200px'>
                    <h4>{station['centro_poblado']}</h4>
                    <b>Operador:</b> {station['operador']}<br>
                    <b>Distancia:</b> {station['distancia']}km<br>
                    <b>Tecnologías:</b> {', '.join(station['tecnologias'])}<br>
                    <b>Velocidad:</b> {station['velocidad']}<br>
                    <b>Ubicación:</b> {station['distrito']}, {station['provincia']}
                </div>
            """
            
            # Agregar marcador al cluster correspondiente
            folium.Marker(
                [station['lat'], station['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=operator_colors.get(operator, 'gray'))
            ).add_to(operator_groups[operator])
        
        # Agregar control de capas
        folium.LayerControl().add_to(m)
        
        # Agregar círculo de radio de búsqueda
        folium.Circle(
            [lat, lon],
            radius=5000,  # 5km en metros
            color='red',
            fill=True,
            opacity=0.1
        ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error en mapa: {str(e)}")
        return None

def create_statistics_plots(df, nearby_stations):
    # Crear visualizaciones con Plotly
    try:
        # Distribución de tecnologías
        tech_data = []
        for station in nearby_stations:
            for tech in station['tecnologias']:
                tech_data.append({'Tecnología': tech, 'Cantidad': 1})
        tech_df = pd.DataFrame(tech_data)
        tech_count = tech_df.groupby('Tecnología').sum().reset_index()

        fig_tech = px.bar(tech_count, 
                         x='Tecnología', 
                         y='Cantidad',
                         title='Distribución de Tecnologías',
                         color='Tecnología')
        
        # Distribución por operador
        operator_data = pd.DataFrame(nearby_stations)
        operator_count = operator_data['operador'].value_counts().reset_index()
        operator_count.columns = ['Operador', 'Cantidad']
        
        fig_operator = px.pie(operator_count, 
                            values='Cantidad', 
                            names='Operador',
                            title='Distribución por Operador')
        
        return fig_tech, fig_operator
    except Exception as e:
        st.error(f"Error en estadísticas: {str(e)}")
        return None, None

def main():
    st.title("🌟 LlamaRural")
    st.subheader("Análisis de Cobertura en Zonas Rurales")
    
    # Cargar datos
    df = load_data()
    if df is None:
        return
    
    # Sidebar
    st.sidebar.header("⚙️ Configuración")
    radius = st.sidebar.slider("Radio de búsqueda (km)", 1, 20, 5)
    operador_filter = st.sidebar.selectbox(
        "Filtrar por operador",
        ["Todos"] + list(df['EMPRESA_OPERADORA'].unique())
    )
    operador_filter = None if operador_filter == "Todos" else operador_filter
    
    # Layout principal
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.subheader("📍 Ubicación")
        
        # Inputs en dos columnas
        loc_col1, loc_col2 = st.columns(2)
        with loc_col1:
            lat = st.number_input("Latitud", value=-12.95197897275646)
        with loc_col2:
            lon = st.number_input("Longitud", value=-76.44419446222732)
        
        if st.button("Analizar Cobertura", type="primary"):
            # Buscar estaciones cercanas
            nearby = find_nearby_stations(df, lat, lon, radius, operador_filter)
            print(nearby)
            if len(nearby) != 0:
                with open('resources/nearby.json', 'w') as file:
                    json.dump(nearby, file, indent=4)
                    print("JSON saved successfully.")
            
            if nearby:
                st.success(f"Se encontraron {len(nearby)} estaciones cercanas")
                
                # Mostrar mapa
                st.subheader("🗺️ Mapa de Cobertura")
                m = create_enhanced_map(lat, lon, nearby)
                if m:
                    folium_static(m)
                
                # Gráficos de estadísticas
                st.subheader("📊 Análisis Detallado")
                fig_tech, fig_operator = create_statistics_plots(df, nearby)
                if fig_tech and fig_operator:
                    st.plotly_chart(fig_tech, use_container_width=True)
                    st.plotly_chart(fig_operator, use_container_width=True)
                
            else:
                st.warning(f"No se encontraron estaciones en un radio de {radius}km")
    
    with col2:
        st.subheader("📊 Estadísticas Globales")
        
        # Métricas en tarjetas
        col_met1, col_met2 = st.columns(2)
        tecnologias = {
            '2G': df['2G'].sum(),
            '3G': df['3G'].sum(),
            '4G': df['4G'].sum(),
            '5G': df['5G'].sum()
        }
        with col_met1:
            st.metric("Total Estaciones", len(df))
            st.metric(f"Estaciones {str('2G')}", tecnologias['2G'])
            st.metric(f"Estaciones {str('4G')}", tecnologias['4G'])
            # st.metric("Cobertura 4G", 
            #          f"{(df['4G'] == 'SI').sum()}/{len(df)}")
        with col_met2:
            st.metric("Total Operadores", 
                     df['EMPRESA_OPERADORA'].nunique())
            st.metric(f"Estaciones {str('3G')}", tecnologias['3G'])
            st.metric(f"Estaciones {str('5G')}", tecnologias['5G'])
            # st.metric("Cobertura 5G", 
            #          f"{(df['5G'] == 'SI').sum()}/{len(df)}")
        
        # Información adicional
        st.subheader("ℹ️ Información")
        st.write("""
        - Los marcadores están agrupados por operador
        - El círculo rojo muestra el radio de búsqueda
        - Puedes filtrar por operador en el panel lateral
        - Ajusta el radio de búsqueda según necesites
        """)

if __name__ == "__main__":
    main()