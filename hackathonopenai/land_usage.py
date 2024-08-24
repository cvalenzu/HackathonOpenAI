import json
from openai import OpenAI
import geopandas
from shapely.geometry import Polygon


class LandUseAssistant:

    def __init__(self, df: geopandas.GeoDataFrame, client: OpenAI):
        self.df = df
        self.client = client

    @staticmethod
    def system_prompt() -> str:
        system_prompt = """
        Eres un experto en uso de suelos y te han contratado para hacer la evaluación de impacto ambiental de un nuevo proyecto fotovoltaico en Chile.

        El usuario entregará la ubicación a validar y los diferentes usos de suelo de la region.

        Tu trabajo es entregar una detallada evaluación de impacto ambiental del proyecto fotovoltaico en las áreas de diferentes usos de suelo cercanas.

        Para esto, primero debes entregar un resumen si encuentras algo crítico para rechazar el proyecto; si no, indica que todo está bien.

        En caso de encontrar algo crítico, debes entregar una evaluación detallada de los impactos ambientales y sociales del proyecto.

        El output será un JSON con dos campos
        ```json
        {
            "emoji": (str) "✅" si no hay problema, "❌" si hay algo critico,
            "resumen": (str) Resumen breve de la evaluacion,
            "evaluacion": (str) Detalle de la evaluacion, agrega un punteo de los distintos aspectos a evaluar en un lenguaje 
                                claro y sencillo para que un usuario sin experiencia tecnica pueda entenderlo.
        }
        ```

        Las categorías de uso de suelo que considerarás son las siguientes: áreas desprovistas de vegetación, praderas y matorrales, humedales, bosque.
        """
        return system_prompt

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
