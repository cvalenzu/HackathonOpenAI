import json
import geopandas 
import folium

from openai import OpenAI
from shapely.geometry import Polygon
import streamlit as st


class PaleontogicalPotentialAssistant:

    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:
        
        
        system_prompt = """
        Eres un experto en potencial paleontologico y te han contratado para hacer la evaluación de impacto ambiental
        de un nuevo proyecto fotovoltaico en Chile.

        El usuario entregará su locacion y los suelos con detalle de potencial paleontologico con los cuales se solapa.

        Tu trabajo es entregar una detallada evaluación de impacto ambiental del proyecto fotovoltaico en esta zona, tomando en cuenta el tipo de potencial.

        Para esto primero vas a entregar un resumen si encuentras algo critico, para rechazar el proyecto, si no di que todo esta bien.

        En caso de que encuentres algo critico, debes entregar una evaluación detallada de los impactos ambientales y sociales del proyecto.

        El output será un JSON con dos campos
        ```json
        {
            "resumen": Resumen corto de la evaluacion,
            "evaluacion": Detalle de la evaluacion
        }
        ```
        """
        return system_prompt

    def format_message(self, overlap_zones: geopandas.GeoDataFrame) -> str:
        overlap_zones_data = str(overlap_zones.to_dict("records"))
        message = """
        las zonas paleontologicas con las que se solapa el suelo son:
        {overlap_zones}
        """
        return message.replace("{overlap_zones}", overlap_zones_data)


    def evaluate_project(self, location: Polygon) -> dict:
            overlap = self.df.geometry.overlaps(location.iloc[0].geometry)
    
            overlap_zones = self.df[ overlap == True]
            
            print("Numero de zonas solapadas: ", overlap_zones.shape[0])
    
            system_prompt = self.system_prompt()
            message = self.format_message(overlap_zones)
    
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
        
            return response_dict
            