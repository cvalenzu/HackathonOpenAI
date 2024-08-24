import folium
import streamlit as st

from openai import OpenAI
from folium.plugins import Draw
from streamlit_folium import st_folium

from shapely.geometry import shape
import geopandas as gpd

from hackathonopenai import (
    NationalMonumentsAssistant, 
    PrioritySitesAssistant
)


from dotenv import load_dotenv
load_dotenv('.env')

client = OpenAI()

# Parques nacionales
df = gpd.read_file('data/parques_nacionales/data_parques.shp')
df_kms = df.to_crs("EPSG:32633")
national_park_expert = NationalMonumentsAssistant(df=df_kms,client=client)


# Sitios prioritarios
df_prioritarios = gpd.read_file('data/sitios_prioritarios/Sitios_Prioritarios.shp')
df_prioritarios_kms = df_prioritarios.to_crs("EPSG:32633")
priority_sites_expert = PrioritySitesAssistant(df=df_prioritarios_kms,client=client)

def generate_report_expert(response: dict, title: str):
    with st.expander(f'**{response["emoji"]} {title}**: {response["resumen"]}'):
        st.write(response["evaluacion"])

        map = response.get('streamlit', None)
        print(map)


def call_agents(gdf: gpd.GeoDataFrame):
    """Call agents to the selected area"""
    response_national_park = national_park_expert.evaluate_project(gdf)
    with st.spinner('Generando informe de Monumentos nacionales...'):
        generate_report_expert(response_national_park, "Monumentos nacionales")

    response_priority_sites = priority_sites_expert.evaluate_project(gdf)
    with st.spinner('Generando informe de Sitios prioritarios...'):
        generate_report_expert(response_priority_sites, "Sitios prioritarios")

st.title('Asistente de evaluación de proyectos fotovoltaicos')
st.write('Welcome to the Home page!')
m = folium.Map(location=[-33.397629, -71.132279], zoom_start=9)
Draw(export=True).add_to(m)

output = st_folium(m, width=1000, height=500)

if st.button('Generar Informe', use_container_width=True):
    geom = output["last_active_drawing"]
    if geom:
        polygon = shape(geom['geometry'])
        gdf = gpd.GeoDataFrame([geom['properties']], geometry=[polygon], crs="EPSG:4326")
        gdf_kms = gdf.to_crs("EPSG:32633")
        call_agents(gdf_kms)
