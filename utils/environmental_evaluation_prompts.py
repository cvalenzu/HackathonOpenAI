# Definition of the JSON format for the output
EVALUATION_JSON_TEMPLATE = """
```json
{
    "emoji": (str) "✅" si no hay problema, "❌" si hay algo crítico,
    "resumen": (str) Resumen breve de la evaluación,
    "evaluacion": (str) Detalle de la evaluación, agrega un punteo de los distintos aspectos a evaluar en un lenguaje claro y sencillo para que un usuario sin experiencia técnica pueda entenderlo.
}
"""

# Common template for prompts, centralizing shared logic to avoid duplication
COMMON_PROMPT_TEMPLATE = """
Eres un experto en {expertise_area} y te han contratado para hacer la evaluación de impacto ambiental de un nuevo proyecto fotovoltaico en Chile.
El usuario entregará la ubicación a validar y los detalles relevantes para tu área de experiencia.
Tu trabajo es entregar una detallada evaluación de impacto ambiental del proyecto fotovoltaico en las áreas cercanas relacionadas con {expertise_area}.
Para esto, primero debes entregar un resumen si encuentras algo crítico para rechazar el proyecto; si no, indica que todo está bien.
En caso de que encuentres algo crítico, debes entregar una evaluación detallada de los impactos ambientales y sociales del proyecto.
El output será un JSON con los siguientes campos: {json_output}
"""


# Function to generate prompts based on the expertise area and specific instructions
def create_evaluation_prompt(
    expertise_area: str,
    specific_guidelines: str,
    json_output_template: str = EVALUATION_JSON_TEMPLATE,
) -> str:
    """
    Generates a prompt based on the area of expertise and specific instructions.

    :param expertise_area: The expert's area of expertise.
    :param specific_guidelines: Specific instructions for the area of expertise.
    :param json_output_template: JSON output format for the evaluation.
    :return: A complete prompt as a string.
    """
    return (
        COMMON_PROMPT_TEMPLATE.format(
            expertise_area=expertise_area, json_output=json_output_template
        )
        + "\n"
        + specific_guidelines
    )
