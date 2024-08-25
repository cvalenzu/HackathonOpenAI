import json
import geopandas 
import folium

from openai import OpenAI
from shapely.geometry import Polygon
import streamlit as st


class NationalMonumentsAssistant:
    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:
        system_prompt = """
        Eres un experto en monumentos nacionales y te han contratado para hacer la evaluación de impacto ambiental
        de un nuevo proyecto fotovoltaico en Chile.

        El usuario entregará su locacion y los monumentos nacionales cercanos, con la distancia en KMs (threshold_in_kilometers)
        No monumentos nacionales tienen que estar a menos de 5Kms del proyecto para ser considerados cercanos, si estan mas lejos
        no son tan relevantes, usa tu conocimiento para definir si es algo critico o no.

        Tu trabajo es entregar una detallada evaluación de impacto ambiental del proyecto fotovoltaico en los monumentos nacionales cercanos.

        Para esto primero vas a entregar un resumen si encuentras algo critico, para rechazar el proyecto, si no di que todo esta bien.

        En caso de que encuentres algo critico, debes entregar una evaluación detallada de los impactos ambientales y sociales del proyecto.

        El output será un JSON con los campos
        ```json
        {
            "emoji": (str) "✅" si no hay problema, "❌" si hay algo critico,
            "resumen": (str) Resumen breve de la evaluacion,
            "evaluacion": (str) Detalle de la evaluacion, agrega un punteo de los distintos aspectos a evaluar en un lenguaje 
                                claro y sencillo para que un usuario sin experiencia tecnica pueda entenderlo.
        }
        ```
        """
        return system_prompt
    
    def format_message(self, close_parks: geopandas.GeoDataFrame) -> str:
        close_parks_data = str(close_parks.to_dict("records"))
        message = """
        Los parques nacionales cercanos a menos de 3km son:
        {close_parks}
        """
        return message.replace("{close_parks}", close_parks_data)


    def evaluate_project(self, location: Polygon, threshold_in_kilometers: int = 10) -> dict:
        distance = self.df.geometry.distance(location.iloc[0].geometry)/1000
        self.df['distance_in_kms'] = distance
        close_parks = self.df[self.df.distance_in_kms < threshold_in_kilometers]        
        print("Numero de parques cercanos: ", close_parks.shape[0])

        system_prompt = self.system_prompt()
        message = self.format_message(close_parks)

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
        response_dict["close_parks"] = close_parks

        if len(close_parks) > 0:
            location.to_crs("EPSG:4326", inplace=True)
            close_parks.to_crs("EPSG:4326", inplace=True)

            centroid = location.centroid.iloc[0]
            center = [centroid.y, centroid.x]

            mapa_national_monument = folium.Map(location=center, zoom_start=12)
            # Agregar los polígonos al mapa
            folium.GeoJson(
                close_parks[['NOMBRE','geometry']],
                style_function=lambda x: {
                    "fillColor": "red",
                    "color": "black",
                    "weight": 2.5,
                    "fillOpacity": 0.5,
                    "tooltip": x['properties']['NOMBRE']
                },
            ).add_to(mapa_national_monument)

            folium.GeoJson(
                location,
                style_function=lambda x: {
                    "fillColor": "blue",
                    "color": "black",
                    "weight": 2.5,
                    "fillOpacity": 0.5,
                    "tooltip": "Proyecto"
                },
            ).add_to(mapa_national_monument)

            response_dict["map"] = mapa_national_monument
        return response_dict
