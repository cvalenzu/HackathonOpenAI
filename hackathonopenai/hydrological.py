import json
import geopandas
import folium

from openai import OpenAI
from shapely.geometry import Polygon
import streamlit as st

from hackathonopenai.constants import JSON_OUTPUT


class HydrologicalAssistant:
    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:
        system_prompt = """
        Eres un experto en hidrografía y su geolocalización, donde se debe preservar la integridad de las redes hídricas de chile y te han contratado para hacer la evaluación de impacto ambiental
        de un nuevo proyecto fotovoltaico en Chile.

        El usuario entregará su locacion y la red hidrográfica de chile.

        Tu trabajo es entregar una detallada evaluación de impacto ambiental del proyecto fotovoltaico en los cuerpos de agua cercanos o que estén dentro del área del proyecto.

        El usuario entregará su locacion y los cuerpos de agua más cercanos, con la en metros (threshold_in_meters)
        los cuerpos de agua tienen que estar a menos de 35 metros del proyecto para ser considerados cercanos, si estan mas lejos
        no son tan relevantes, usa tu conocimiento para definir si es algo critico o no. Por otro lado si el cuerpo de agua se intersecta con el polygono del proyecto 
        (la distancia es 0), podría sugerir modificar el polygono del proyecto dado que es más probable que sea rechazado, o 
        también incurrir en permisos ambientales sectoriales y recomienda cuales usar.

        Tu trabajo es entregar una detallada evaluación de impacto ambiental del proyecto fotovoltaico en los cuerpos de agua cercanos.

        Para esto primero vas a entregar un resumen si encuentras algo critico, para rechazar el proyecto, si no di que todo esta bien.

        En caso de que encuentres algo critico, debes entregar una evaluación detallada de los impactos ambientales y sociales del proyecto.

        El output será un JSON con los campos
        {JSON_OUTPUT}
        """
        return system_prompt
    
    def format_message(self, close_hyd: geopandas.GeoDataFrame) -> str:
        close_hyd_data = str(close_hyd.to_dict("records"))
        message = """
        Los cuerpos de agua cercanos a menos de 35 m son:
        {close_hyd}
        """
        return message.replace("{close_hyd}", close_hyd_data)


    def evaluate_project(self, location: Polygon, threshold_in_meters: int = 35) -> dict:
        distance = self.df.geometry.distance(location.iloc[0].geometry.exterior)
        self.df['distance_in_mts'] = distance
        close_hyd = self.df[self.df.distance_in_mts < threshold_in_meters]        
        print("Numero de cuerpos de agua cercanos: ", close_hyd.shape[0])

        system_prompt = self.system_prompt()
        message = self.format_message(close_hyd)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={ "type": "json_object" },
            temperature=0
        )
        response_dict = json.loads(response.choices[0].message.content)

        if len(close_hyd) > 0:
            pass
            # # Create a map with the close parks with folium
            # mapa = folium.Map(location=[-33.397629, -71.132279], zoom_start=10)
            # # Agregar los polígonos al mapa
            # folium.GeoJson(
            #     close_parks[['NOMBRE','geometry']],
            #     style_function=lambda x: {
            #         "fillColor": "blue",
            #         "color": "black",
            #         "weight": 2.5,
            #         "fillOpacity": 0.5,
            #     },
            # ).add_to(mapa)
            # response_dict["streamlit"] = st.markdown(mapa._repr_html_(), unsafe_allow_html=True)
        return response_dict