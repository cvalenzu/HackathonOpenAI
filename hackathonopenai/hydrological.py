import json

import geopandas
from openai import OpenAI
from shapely.geometry import Polygon

from utils.environmental_evaluation_prompts import create_evaluation_prompt


class HydrologicalAssistant:
    
    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:
        return create_evaluation_prompt(
            expertise_area="hidrografía",
            specific_guidelines="El usuario entregará su ubicación y la red hidrográfica de Chile. Considera cuerpos de agua cercanos, usando 35 metros como umbral. Si el proyecto se intersecta con un cuerpo de agua, sugiere modificar el polígono o recomienda permisos ambientales sectoriales específicos.",
        )

    def format_message(self, close_hyd: geopandas.GeoDataFrame) -> str:
        close_hyd_data = str(close_hyd.to_dict("records"))
        message = """
        Los cuerpos de agua cercanos a menos de 35 m son:
        {close_hyd}
        """
        return message.replace("{close_hyd}", close_hyd_data)

    def evaluate_project(
        self, location: Polygon, threshold_in_meters: int = 35
    ) -> dict:
        distance = self.df.geometry.distance(location.iloc[0].geometry.exterior)
        self.df["distance_in_mts"] = distance
        close_hyd = self.df[self.df.distance_in_mts < threshold_in_meters]
        print("Numero de cuerpos de agua cercanos: ", close_hyd.shape[0])

        system_prompt = self.system_prompt()
        message = self.format_message(close_hyd)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
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
