import json

import geopandas
from openai import OpenAI
from shapely.geometry import Polygon

from utils.environmental_evaluation_prompts import create_evaluation_prompt


class PaleontogicalPotentialAssistant:

    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:
        return create_evaluation_prompt(
            expertise_area="potencial paleontológico",
            specific_guidelines="Considera los suelos con potencial paleontológico en los cuales se solapa el proyecto.",
        )

    def format_message(self, overlap_zones: geopandas.GeoDataFrame) -> str:
        overlap_zones_data = str(overlap_zones.to_dict("records"))
        message = """
        las zonas paleontologicas con las que se solapa el suelo son:
        {overlap_zones}
        """
        return message.replace("{overlap_zones}", overlap_zones_data)

    def evaluate_project(self, location: Polygon) -> dict:
        overlap = self.df.geometry.overlaps(location.iloc[0].geometry)

        overlap_zones = self.df[overlap == True]

        print("Numero de zonas solapadas: ", overlap_zones.shape[0])

        system_prompt = self.system_prompt()
        message = self.format_message(overlap_zones)

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
