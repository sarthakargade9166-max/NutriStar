"""Diet analysis and recommendations using Gemini AI."""

import json

DIET_ANALYSIS_PROMPT = """You are a nutrition analyst for an Indian food tracking app.

Analyze the user's daily nutrition intake vs targets. Provide:
1. Gap analysis (which macros need attention)
2. Actionable Indian food recommendations
3. Be encouraging but honest
4. Never diagnose diseases or prescribe medication
5. These are general nutrition suggestions, not medical advice

Focus on: protein adequacy (common gap in Indian diets), balanced macros, practical Indian food suggestions.

Return JSON:
{
  "summary": "1-2 sentence analysis",
  "priority": "protein"|"calories"|"fat"|"carbs"|"balanced",
  "insights": [{"title": "...", "content": "2-3 sentences", "type": "protein_gap|calorie_pattern|meal_balance|recommendation"}],
  "recommendations": [{"food": "name", "quantity": "e.g. 1 bowl", "reason": "why"}]
}"""


def analyze_diet(context: dict, api_key: str) -> dict:
    """Analyze diet data and return insights + recommendations."""
    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f'{DIET_ANALYSIS_PROMPT}\n\nAnalyze:\n{json.dumps(context, indent=2)}',
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.3,
            }
        )
        return json.loads(response.text)
    except Exception as e:
        return {'error': str(e), 'summary': 'Analysis unavailable.', 'insights': [], 'recommendations': []}
