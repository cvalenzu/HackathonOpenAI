import json
import geopandas 
from openai import OpenAI
from shapely.geometry import Polygon

class PrioritySitesAssistant:

    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    def system_prompt(self) -> str:        
        system_prompt = """
        Eres un experto en sitios prioritarios de alta importancia para la conservación ambiental, protección de la biodiversidad, 
        o preservación de ciertos recursos naturales o culturales y te han contratado para hacer la evaluación de impacto ambiental
        de un nuevo proyecto de parque fotovoltaico en Chile bajo su respectiva legislación.

        El usuario entregará su locacion y los sitios prioritarios cercanos en un radio de 3km.

        Tu trabajo es entregar una detallada evaluación de impacto ambiental del proyecto fotovoltaico en los sitios prioritarios cercanos.

        Para esto primero vas a entregar un resumen si encuentras algo critico, para rechazar el proyecto, si no di que todo esta bien.

        En caso de que encuentres algo critico, debes entregar una evaluación detallada de los impactos ambientales y sociales del proyecto.

        El output será un JSON con dos campos
        ```json
        {
            "emoji": (str) "✅" si no hay problema, "⚠️" si hay algo cercano, "❌" si hay algo critico,
            "resumen": (str) Resumen breve de la evaluacion,
            "evaluacion": (str) Detalle de la evaluacion, agrega un punteo de los distintos aspectos a evaluar en un lenguaje 
                                claro y sencillo para que un usuario sin experiencia tecnica pueda entenderlo.
        }
        ```
        """
        return system_prompt
    
    def format_message(self, close_sites: geopandas.GeoDataFrame) -> str:
        close_sites_data = str(close_sites.to_dict("records"))
        message = """
        Los sitios prioritarios cercanos a menos de 3km son:
        {close_sites}
        """
        return message.replace("{close_sites}", close_sites_data)


    def evaluate_project(self, location: Polygon, threshold_in_meters: int = 3000) -> dict:
        distance = self.df.geometry.distance(location.iloc[0].geometry)

        close_parks = self.df[distance < threshold_in_meters]
        
        print("Numero de sitios cercanos: ", close_parks.shape[0])

        system_prompt = self.system_prompt()
        message = self.format_message(close_parks)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={ "type": "json_object" },
            temperature=0
        )
        return json.loads(response.choices[0].message.content)