import streamlit as st 
import pandas as pd
import folium
import json
from streamlit_folium import folium_static
import numpy as np
import plotly.express as px
from folium.plugins import HeatMap, MarkerCluster, Search
from branca.colormap import LinearColormap

# Page configuration

st.set_page_config(
    page_title="LlamaRural - Coverage Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'nearby_stations' not in st.session_state:
    st.session_state.nearby_stations = None

# Custom style
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

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('resources/MOBILE_SERVICE_COVERAGE_BY_COMPANY.csv', 
                        sep=';', 
                        encoding='latin-1')
        
        # Calculate available technologies
        df['technologies'] = df.apply(lambda x: [tech for tech, val in 
            zip(['2G', '3G', '4G', '5G'], [x['2G'], x['3G'], x['4G'], x['5G']]) 
            if val == 'YES'], axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Improved function to find nearby stations
def find_nearby_stations(df, lat, lon, radius_km=5, operator_filter=None):
    try:
        # Calculate distances using numpy
        df['distance'] = np.sqrt(
            (df['LATITUD'] - lat)**2 + 
            (df['LONGITUD'] - lon)**2
        ) * 111  # Approximate conversion to kilometers
        
        # Apply filters
        mask = df['distance'] <= radius_km
        if operator_filter:
            mask &= df['EMPRESA_OPERADORA'] == operator_filter
            
        nearby_df = df[mask].copy()
        
        # Convert to list of dictionaries
        nearby = []
        for _, row in nearby_df.iterrows():
            techs = [tech for tech, val in 
                    zip(['2G', '3G', '4G', '5G'], 
                        [row['2G'], row['3G'], row['4G'], row['5G']]) 
                    if val == 1]
            
            nearby.append({
                'distance': round(row['distance'], 2),
                'CENTRO_POBLADO': row['CENTRO_POBLADO'],
                'operator': row['EMPRESA_OPERADORA'],
                'department': row['DEPARTAMENTO'],
                'province': row['PROVINCIA'],
                'district': row['DISTRITO'],
                'lat': row['LATITUD'],
                'lon': row['LONGITUD'],
                'technologies': techs,
                'speed': 'More than 1Mbps' if row['MÁS_DE_1_MBPS'] == 1 else 'Up to 1Mbps'
            })
        
        return nearby
    except Exception as e:
        st.error(f"Error in search: {str(e)}")
        return []

def create_enhanced_map(lat, lon, nearby_stations):
    try:
        m = folium.Map(location=[lat, lon], zoom_start=12)
        
        # Create groups of markers by operator
        operator_groups = {}
        
        # Colors by operator
        operator_colors = {
            'TELEFÓNICA DEL PERÚ S.A.A.': 'blue',
            'AMÉRICA MÓVIL PERÚ S.A.C.': 'red',
            'VIETTEL PERÚ S.A.C.': 'green',
            'ENTEL PERÚ S.A.': 'purple'
        }
        
        # User marker
        folium.Marker(
            [lat, lon],
            popup="Your location",
            icon=folium.Icon(color='black', icon='home')
        ).add_to(m)
        
        # Create clusters by operator
        for station in nearby_stations:
            operator = station['operator']
            if operator not in operator_groups:
                operator_groups[operator] = MarkerCluster(name=operator)
                operator_groups[operator].add_to(m)
            
            # Create popup with detailed information
            popup_html = f"""
                <div style='width:200px'>
                    <h4>{station['CENTRO_POBLADO']}</h4>
                    <b>Operator:</b> {station['operator']}<br>
                    <b>Distance:</b> {station['distance']}km<br>
                    <b>Technologies:</b> {', '.join(station['technologies'])}<br>
                    <b>Speed:</b> {station['speed']}<br>
                    <b>Location:</b> {station['district']}, {station['province']}
                </div>
            """
            
            # Add marker to the corresponding cluster
            folium.Marker(
                [station['lat'], station['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=operator_colors.get(operator, 'gray'))
            ).add_to(operator_groups[operator])
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add search radius circle
        folium.Circle(
            [lat, lon],
            radius=5000,  # 5km in meters
            color='red',
            fill=True,
            opacity=0.1
        ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error in map: {str(e)}")
        return None

def create_statistics_plots(df, nearby_stations):
    # Create visualizations with Plotly
    try:
        # Technology distribution
        tech_data = []
        for station in nearby_stations:
            for tech in station['technologies']:
                tech_data.append({'Technology': tech, 'Count': 1})
        tech_df = pd.DataFrame(tech_data)
        tech_count = tech_df.groupby('Technology').sum().reset_index()

        fig_tech = px.bar(tech_count, 
                         x='Technology', 
                         y='Count',
                         title='Technology Distribution',
                         color='Technology')
        
        # Distribution by operator
        operator_data = pd.DataFrame(nearby_stations)
        operator_count = operator_data['operator'].value_counts().reset_index()
        operator_count.columns = ['Operator', 'Count']
        
        fig_operator = px.pie(operator_count, 
                            values='Count', 
                            names='Operator',
                            title='Distribution by Operator')
        
        return fig_tech, fig_operator
    except Exception as e:
        st.error(f"Error in statistics: {str(e)}")
        return None, None

def main():
    st.title("🌟 LlamaRural")
    st.subheader("Coverage Analysis in Rural Areas")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    radius = st.sidebar.slider("Search Radius (km)", 1, 20, 5)
    operator_filter = st.sidebar.selectbox(
        "Filter by operator",
        ["All"] + list(df['EMPRESA_OPERADORA'].unique())
    )
    operator_filter = None if operator_filter == "All" else operator_filter
    
    # Main layout
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.subheader("📍 Location")
        
        # Inputs in two columns
        loc_col1, loc_col2 = st.columns(2)
        with loc_col1:
            lat = st.number_input("Latitude", value=-12.95197897275646)
        with loc_col2:
            lon = st.number_input("Longitude", value=-76.44419446222732)
        
        if st.button("Analyze Coverage", type="primary"):
            # Search for nearby stations
            nearby = find_nearby_stations(df, lat, lon, radius, operator_filter)
            print(nearby)
            if len(nearby) != 0:
                with open('resources/nearby.json', 'w') as file:
                    json.dump(nearby, file, indent=4)
                    print("JSON saved successfully.")
            
            if nearby:
                st.success(f"{len(nearby)} nearby stations found")
                
                # Show map
                st.subheader("🗺️ Coverage Map")
                m = create_enhanced_map(lat, lon, nearby)
                if m:
                    folium_static(m)
                
                # Statistics plots
                st.subheader("📊 Detailed Analysis")
                fig_tech, fig_operator = create_statistics_plots(df, nearby)
                if fig_tech and fig_operator:
                    st.plotly_chart(fig_tech, use_container_width=True)
                    st.plotly_chart(fig_operator, use_container_width=True)
                
            else:
                st.warning(f"No stations found within a {radius}km radius")
    
    with col2:
        st.subheader("📊 Global Statistics")
        
        # Metrics in cards
        col_met1, col_met2 = st.columns(2)
        technologies = {
            '2G': df['2G'].sum(),
            '3G': df['3G'].sum(),
            '4G': df['4G'].sum(),
            '5G': df['5G'].sum()
        }
        with col_met1:
            st.metric("Total Stations", len(df))
            st.metric(f"Stations {str('2G')}", technologies['2G'])
            st.metric(f"Stations {str('4G')}", technologies['4G'])
            # st.metric("4G Coverage", 
            #          f"{(df['4G'] == 'YES').sum()}/{len(df)}")
        with col_met2:
            st.metric("Total Operators", 
                     df['EMPRESA_OPERADORA'].nunique())
            st.metric(f"Stations {str('3G')}", technologies['3G'])
            st.metric(f"Stations {str('5G')}", technologies['5G'])
            # st.metric("5G Coverage", 
            #          f"{(df['5G'] == 'YES').sum()}/{len(df)}")
        
        # Additional information
        st.subheader("ℹ️ Information")
        st.write("""
        - Markers are grouped by operator
        - The red circle shows the search radius
        - You can filter by operator in the sidebar
        - Adjust the search radius as needed
        """)

if __name__ == "__main__":
    main()
