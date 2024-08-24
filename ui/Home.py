import folium
import streamlit as st

from folium.plugins import Draw
from streamlit_folium import st_folium

from shapely.geometry import shape
import geopandas as gpd


def call_agents(gdf: gpd.GeoDataFrame):
    st.write('Calling agents...')
    print(gdf)
    st.write('Agents called!')



def app():
    st.title('Home')
    st.write('Welcome to the Home page!')
    m = folium.Map(location=[-33.397629, -71.132279], zoom_start=9  )
    Draw(export=True).add_to(m)

    output = st_folium(m, width=700, height=500)
    if output["last_active_drawing"] is not None:
        geom = output["last_active_drawing"]
        polygon = shape(geom['geometry'])
        gdf = gpd.GeoDataFrame([geom['properties']], geometry=[polygon], crs="EPSG:4326")

        if st.button('Generar Informe', use_container_width=True):
            call_agents(gdf)


if __name__ == '__main__':
    app()