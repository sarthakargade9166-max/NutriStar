"""Unit conversion — household Indian units to grams with food-specific awareness."""

from typing import Optional, Dict, Any

UNIT_GRAMS = {
    'g': 1.0,
    'gram': 1.0,
    'grams': 1.0,
    'kg': 1000.0,
    'kilogram': 1000.0,
    'kilograms': 1000.0,
    'ml': 1.0,
    'milliliter': 1.0,
    'milliliters': 1.0,
    'l': 1000.0,
    'liter': 1000.0,
    'liters': 1000.0,
    'piece': 50.0,
    'pieces': 50.0,
    'bowl': 150.0,
    'bowls': 150.0,
    'katori': 150.0,
    'cup': 240.0,
    'cups': 240.0,
    'glass': 250.0,
    'glasses': 250.0,
    'tablespoon': 15.0,
    'tablespoons': 15.0,
    'tbsp': 15.0,
    'teaspoon': 5.0,
    'teaspoons': 5.0,
    'tsp': 5.0,
    'plate': 300.0,
    'plates': 300.0,
    'serving': 150.0,
    'servings': 150.0,
    'slice': 30.0,
    'slices': 30.0,
    'container': 250.0,
    'containers': 250.0,
    'pack': 250.0,
    'packet': 250.0,
}


def convert_to_grams(quantity: float, unit: str, food_name: str = '', food: Optional[Dict[str, Any]] = None) -> float:
    """Convert a quantity + unit to grams, using food-specific metrics when available."""
    lower_unit = (unit or 'serving').lower().strip()

    # Exact standard weight/volume units
    if lower_unit in ('g', 'gram', 'grams', 'ml', 'milliliter', 'milliliters'):
        return quantity * 1.0
    if lower_unit in ('kg', 'kilogram', 'kilograms', 'l', 'liter', 'liters'):
        return quantity * 1000.0

    if food:
        # 1. Exact food serving unit match
        food_serving_unit = (food.get('serving_unit') or food.get('servingUnit') or '').lower().strip()
        if lower_unit == food_serving_unit:
            grams_per_serving = float(food.get('grams_per_serving') or food.get('gramsPerServing') or 100)
            return quantity * grams_per_serving

        # 2. Piece conversion using food-specific grams_per_piece
        if lower_unit in ('piece', 'pieces'):
            if food.get('grams_per_piece') is not None or food.get('gramsPerPiece') is not None:
                per_piece = float(food.get('grams_per_piece') if food.get('grams_per_piece') is not None else food.get('gramsPerPiece'))
                return quantity * per_piece
            if food_serving_unit in ('piece', 'pieces'):
                return quantity * float(food.get('grams_per_serving') or food.get('gramsPerServing') or 50)

        # 3. Cup conversion using food-specific grams_per_cup or ml_per_cup
        if lower_unit in ('cup', 'cups'):
            if food.get('category') == 'beverages' or food.get('serving_type') == 'liquid' or food.get('servingType') == 'liquid':
                if food.get('ml_per_cup') or food.get('mlPerCup'):
                    return quantity * float(food.get('ml_per_cup') or food.get('mlPerCup'))
            if food.get('grams_per_cup') or food.get('gramsPerCup'):
                return quantity * float(food.get('grams_per_cup') or food.get('gramsPerCup'))

        # 4. Container / Pack conversion
        if lower_unit in ('container', 'containers', 'pack', 'packet'):
            if food.get('grams_per_serving') or food.get('gramsPerServing'):
                return quantity * float(food.get('grams_per_serving') or food.get('gramsPerServing'))

    # Fallback to general household units table
    factor = UNIT_GRAMS.get(lower_unit, 100.0)
    return quantity * factor
