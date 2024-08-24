import json
import geopandas 
from openai import OpenAI
from shapely.geometry import Polygon


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

        El output será un JSON con dos campos
        ```json
        {
            "emoji": (str) "✅" si no hay problema, "❌" si hay algo critico,
            "resumen": (str) Resumen corto de la evaluacion,
            "evaluacion": (str) Detalle de la evaluacion
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
        print(close_parks)
        
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
        return json.loads(response.choices[0].message.content)