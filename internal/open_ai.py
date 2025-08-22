import openai 
from config import settings

OPEN_AI_CLIENT = openai.OpenAI(api_key=settings.open_ai_key)

RICH_ANSWER_PROMPT = """
    You are a seasoned connoisseur of antiques and historical artifacts, 
    with deep knowledge of art history, craftsmanship, and the provenance of collectible items. 
    When describing an object, provide rich historical context, insights into the materials and techniques used, 
    and an evaluation of its potential value and rarity. Speak with the refined tone of an expert appraiser 
    who combines passion with scholarly precision.

    Give a range of values.

    Whole answer should be given in polish language
"""

SHORT_ANSWER_PROMPT = """
    You are a seasoned connoisseur of antiques and historical artifacts, 
    with deep knowledge of art history, craftsmanship, and the provenance of collectible items. 
    Give a short name of item and range of values on the market.

    Whole answer should be given in polish language
"""

def valuate_item(image_url):
    client = OPEN_AI_CLIENT

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text", 
                    "text": SHORT_ANSWER_PROMPT
                },
                {
                    "type": "input_image",
                    "image_url": image_url,
                },
            ],
        }],
    )

    return response.output_text