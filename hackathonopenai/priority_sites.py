import json

import geopandas
from openai import OpenAI
from shapely.geometry import Polygon

from utils.environmental_evaluation_prompts import create_evaluation_prompt


class PrioritySitesAssistant:

    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:
        return create_evaluation_prompt(
            expertise_area="sitios prioritarios",
            specific_guidelines="Considera sitios prioritarios en un radio de 3 km del proyecto.",
        )

    def format_message(self, close_sites: geopandas.GeoDataFrame) -> str:
        close_sites_data = str(close_sites.to_dict("records"))
        message = """
        Los sitios prioritarios cercanos a menos de 3km son:
        {close_sites}
        """
        return message.replace("{close_sites}", close_sites_data)

    def evaluate_project(
        self, location: Polygon, threshold_in_meters: int = 3000
    ) -> dict:
        distance = self.df.geometry.distance(location.iloc[0].geometry)

        close_parks = self.df[distance < threshold_in_meters]

        print("Numero de sitios cercanos: ", close_parks.shape[0])

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
        return json.loads(response.choices[0].message.content)
