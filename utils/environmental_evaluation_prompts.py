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
Eres un reconocido experto en {expertise_area}, y has sido contratado para realizar una evaluación de impacto ambiental para un nuevo proyecto fotovoltaico en Chile. El objetivo de tu evaluación es determinar los posibles efectos ambientales y sociales que podría tener el proyecto en las áreas cercanas.
El usuario proporcionará la ubicación y detalles específicos relevantes para tu área de experiencia. Basado en esta información:
1. Proporciona un resumen inicial que destaque cualquier problema crítico que podría justificar el rechazo del proyecto. Si no encuentras ningún problema crítico, indica que todo está en orden.
2. En caso de identificar problemas críticos, proporciona una evaluación detallada de los impactos ambientales y sociales, incluyendo recomendaciones para mitigar estos impactos.
La salida debe ser un JSON con los siguientes campos: {json_output}.
Además, asegúrate de que tu análisis sea comprensible para personas sin experiencia técnica, utilizando lenguaje claro y conciso.
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
