import json

import folium
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
        response_dict["close_parks"] = close_parks

        if len(close_parks) > 0:
            location.to_crs("EPSG:4326", inplace=True)
            close_parks.to_crs("EPSG:4326", inplace=True)

            centroid = location.centroid.iloc[0]
            center = [centroid.y, centroid.x]

            mapa_national_monument = folium.Map(location=center, zoom_start=12)
            # Agregar los polígonos al mapa
            folium.GeoJson(
                close_parks[["NOMBRE", "geometry"]],
                style_function=lambda x: {
                    "fillColor": "red",
                    "color": "black",
                    "weight": 2.5,
                    "fillOpacity": 0.5,
                    "tooltip": x["properties"]["NOMBRE"],
                },
            ).add_to(mapa_national_monument)

            folium.GeoJson(
                location,
                style_function=lambda x: {
                    "fillColor": "blue",
                    "color": "black",
                    "weight": 2.5,
                    "fillOpacity": 0.5,
                    "tooltip": "Proyecto",
                },
            ).add_to(mapa_national_monument)

            response_dict["map"] = mapa_national_monument
        return response_dict
