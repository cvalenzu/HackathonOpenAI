import json

import geopandas
from openai import OpenAI
from shapely.geometry import Polygon

from utils.environmental_evaluation_prompts import create_evaluation_prompt


class NationalMonumentsAssistant:

    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:
        return create_evaluation_prompt(
            expertise_area="monumentos nacionales",
            specific_guidelines="Los monumentos nacionales considerados deben estar a menos de 5 km del proyecto para ser relevantes.",
        )

    def format_message(self, close_parks: geopandas.GeoDataFrame) -> str:
        close_parks_data = str(close_parks.to_dict("records"))
        message = """
        Los parques nacionales cercanos a menos de 3km son:
        {close_parks}
        """
        return message.replace("{close_parks}", close_parks_data)

    def evaluate_project(
        self, location: Polygon, threshold_in_kilometers: int = 10
    ) -> dict:
        distance = self.df.geometry.distance(location.iloc[0].geometry) / 1000
        self.df["distance_in_kms"] = distance
        close_parks = self.df[self.df.distance_in_kms < threshold_in_kilometers]
        print("Numero de parques cercanos: ", close_parks.shape[0])

        system_prompt = self.system_prompt()
        message = self.format_message(close_parks)

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

        if len(close_parks) > 0:
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
