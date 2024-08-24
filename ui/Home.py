import folium
import geopandas as gpd
import streamlit as st
from dotenv import load_dotenv
from folium.plugins import Draw
from openai import OpenAI
from shapely.geometry import shape
from streamlit_folium import st_folium

from hackathonopenai import (
    NationalMonumentsAssistant,
    PrioritySitesAssistant
)
from hackathonopenai.land_usage import LandUseAssistant

load_dotenv('.env')

client = OpenAI()

@st.cache_data
def load_assistants():
    # Parques nacionales
    df = gpd.read_file('data/parques_nacionales/data_parques.shp')
    df_kms = df.to_crs("EPSG:32633")

    # Sitios prioritarios
    df_prioritarios = gpd.read_file('data/sitios_prioritarios/Sitios_Prioritarios.shp')
    df_prioritarios_kms = df_prioritarios.to_crs("EPSG:32633")

    # Uso de suelos
    df_land_usage = gpd.read_file('data/uso_suelos/05_region_valparaiso.shp')[
        ["USO_TIERRA", "USO", "NOM_REG", "NOM_COM", "geometry"]]
    df_land_usage_kms = df_land_usage.to_crs("EPSG:32633")
    return {
        "national_park_expert_data": df_kms,
        "priority_sites_expert_data": df_prioritarios_kms,
        "land_usage_expert_data": df_land_usage_kms
    }

experts = load_assistants()
national_monument_expert = NationalMonumentsAssistant(df=experts['national_park_expert_data'], client=client)
priority_sites_expert = PrioritySitesAssistant(df=experts['priority_sites_expert_data'], client=client)
land_usage_expert = LandUseAssistant(df=experts['land_usage_expert_data'], client=client)

def generate_report_expert(response: dict, title: str):
    with st.expander(f'**{response["emoji"]} {title}**: {response["resumen"]}'):
        st.write(response["evaluacion"])

def call_agents(gdf: gpd.GeoDataFrame):
    """Call agents to the selected area"""
    response_national_park = national_monument_expert.evaluate_project(gdf)
    with st.spinner('Generando informe de Monumentos nacionales...'):
        generate_report_expert(response_national_park, "Monumentos nacionales")

    response_priority_sites = priority_sites_expert.evaluate_project(gdf)
    with st.spinner('Generando informe de Sitios prioritarios...'):
        generate_report_expert(response_priority_sites, "Sitios prioritarios")

    response_land_usage = land_usage_expert.evaluate_project(gdf)
    with st.spinner('Generando informe de Sitios prioritarios...'):
        generate_report_expert(response_land_usage, "Uso de suelos protegidos")


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
