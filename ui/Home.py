import folium
import geopandas as gpd
import streamlit as st
from dotenv import load_dotenv
from folium.plugins import Draw
from openai import OpenAI
from shapely.geometry import shape
from streamlit_folium import st_folium, folium_static

from hackathonopenai import (
    NationalMonumentsAssistant,
    PaleontogicalPotentialAssistant,
    PrioritySitesAssistant,
    HydrologicalAssistant,
)
from hackathonopenai.land_usage import LandUseAssistant

# Constants
UTM_CRS = "EPSG:32633"
NATIONAL_PARKS_PATH = "data/parques_nacionales/data_parques.shp"
PRIORITY_SITES_PATH = "data/sitios_prioritarios/Sitios_Prioritarios.shp"
LAND_USAGE_PATH = "data/uso_suelos/05_region_valparaiso.shp"
PALEONTOLOGICAL_PATH = "data/potencial_paleontologico/data_pot_paleon.shp"
HYDROLOGICAL_PATH = "data/hidro/data_hidro.shp"

load_dotenv(".env")

client = OpenAI()

st.set_page_config(layout="wide")


@st.cache_data
def load_assistants():
    # Load geospatial data
    df_national_monuments = load_geospatial_data(NATIONAL_PARKS_PATH)
    df_prioritarios = load_geospatial_data(PRIORITY_SITES_PATH)
    df_land_usage = load_geospatial_data(
        LAND_USAGE_PATH, columns=["USO_TIERRA", "USO", "NOM_REG", "NOM_COM", "geometry"]
    )
    df_palentological = load_geospatial_data(PALEONTOLOGICAL_PATH)
    df_hydrological = load_geospatial_data(HYDROLOGICAL_PATH)

    return {
        "national_park_expert_data": df_national_monuments,
        "priority_sites_expert_data": df_prioritarios,
        "land_usage_expert_data": df_land_usage,
        "paleontological_potential_expert_data": df_palentological,
        "hydrological_expert_data": df_hydrological,
    }


def load_geospatial_data(filepath, columns=None):
    """Load and reproject geospatial data."""
    try:
        df = gpd.read_file(filepath)
        if columns:
            df = df[columns]
        return df.to_crs(UTM_CRS)
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
        return None


# Initialize experts
experts = load_assistants()
national_monument_expert = NationalMonumentsAssistant(
    df=experts["national_park_expert_data"], client=client
)
priority_sites_expert = PrioritySitesAssistant(
    df=experts["priority_sites_expert_data"], client=client
)
land_usage_expert = LandUseAssistant(
    df=experts["land_usage_expert_data"], client=client
)
paleontological_potential_expert = PaleontogicalPotentialAssistant(
    df=experts["paleontological_potential_expert_data"], client=client
)
hydrological_expert = HydrologicalAssistant(
    df=experts["hydrological_expert_data"], client=client
)


def generate_report_expert(response: dict, title: str):
    """Generates the report for each expert's evaluation."""
    with st.expander(f'**{response["emoji"]} {title}**: {response["resumen"]}'):
        st.write(response["evaluacion"])
        if map:=response.get("map"):
            folium_static(map, width=620, height=200)


def call_agents(gdf: gpd.GeoDataFrame):
    """Call agents to the selected area."""
    experts = [
        ("Monumentos nacionales", national_monument_expert),
        ("Sitios prioritarios", priority_sites_expert),
        ("Uso de suelos protegidos", land_usage_expert),
        ("Potencial paleontológico", paleontological_potential_expert),
        ("Hidrografía", hydrological_expert),
    ]

    for title, expert in experts:
        with st.spinner(f"Generando informe de {title}..."):
            response = expert.evaluate_project(gdf.copy())
            generate_report_expert(response, title)


st.title("Camilo y Los fotovoltaicos")
st.write(
    "Bienvenido a la página de evaluación de impacto ambiental para proyectos fotovoltaicos."
)

col1, col2 = st.columns(2)

with col1:
    m = folium.Map(location=[-33.397629, -71.132279], zoom_start=9)
    Draw(export=True).add_to(m)

    output = st_folium(m, width=1000, height=500)
    btn_report = st.button("Generar Informe", use_container_width=True)

with col2:
    if btn_report:
        geom = output.get("last_active_drawing")
        if geom:
            polygon = shape(geom["geometry"])
            gdf = gpd.GeoDataFrame(
                [geom["properties"]], geometry=[polygon], crs="EPSG:4326"
            )
            gdf_kms = gdf.to_crs("EPSG:32633")
            call_agents(gdf_kms)
        else:
            st.warning(
                "Por favor, dibuja un polígono en el mapa antes de generar el informe."
            )
