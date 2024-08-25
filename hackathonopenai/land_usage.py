import json

import geopandas
from openai import OpenAI
from shapely.geometry import Polygon

from utils.environmental_evaluation_prompts import create_evaluation_prompt


class LandUseAssistant:

    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    @staticmethod
    def system_prompt() -> str:
        return create_evaluation_prompt(
            expertise_area="uso de suelos",
            specific_guidelines="Las categorías de uso de suelo que considerarás son las siguientes: áreas desprovistas de vegetación, praderas y matorrales, humedales, bosque.",
        )

    @staticmethod
    def format_message(nearby_land_use: geopandas.GeoDataFrame) -> str:
        nearby_land_use_data = str(nearby_land_use.to_dict("records"))
        message = """
        Los tipos de uso de suelo dentro de un radio de 3 km de la ubicación del proyecto son:
        {nearby_land_use}
        """
        return message.replace("{nearby_land_use}", nearby_land_use_data)

    def evaluate_project(self, location: Polygon) -> dict:
        overlaps = self.df[self.df.geometry.overlaps(location.iloc[0].geometry)]
        print(
            "# de cruces del poligono con uso de suelo protegido: ", overlaps.shape[0]
        )

        system_prompt = self.system_prompt()
        message = self.format_message(overlaps)

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
        return response_dict
