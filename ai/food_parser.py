"""Natural language food parser using Gemini AI."""

import json

FOOD_PARSE_PROMPT = """You are a food parsing assistant for an Indian food nutrition tracker.
Convert natural language food descriptions into structured JSON.

Rules:
1. Extract each food item with quantity and unit
2. If no quantity, assume 1 serving
3. If no unit, use 'serving' or 'piece' as appropriate
4. Recognize Indian food names (Hindi, regional)
5. Detect meal type from context
6. Units: g, piece, bowl, cup, glass, tablespoon, teaspoon, plate, serving, ml

Common aliases: roti/chapati/phulka, dahi=curd, chawal=rice, dal/daal=lentil, paneer=cottage cheese, chai=tea

Return JSON:
{
  "meal_type": "breakfast"|"lunch"|"snack"|"dinner"|null,
  "foods": [{"name": "food name", "quantity": number, "unit": "unit"}]
}"""


def parse_food_input(input_text: str, api_key: str) -> dict:
    """Parse natural language food input into structured data."""
    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f'{FOOD_PARSE_PROMPT}\n\nParse this: "{input_text}"',
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.1,
            }
        )
        return json.loads(response.text)
    except Exception as e:
        return {'error': str(e), 'foods': []}
