"""Nutrition calculator — all math is per 100g based."""

from nutrition.units import convert_to_grams


def calculate_food_nutrition(food: dict, quantity: float, unit: str = 'g') -> dict:
    """Calculate nutrition for a given food, quantity, and unit."""
    if unit == 'g':
        grams = quantity
    elif unit == food.get('serving_unit'):
        grams = quantity * food.get('grams_per_serving', 100)
    else:
        grams = convert_to_grams(quantity, unit)

    multiplier = grams / 100
    return {
        'calories': round(food['calories_per_100g'] * multiplier, 1),
        'protein': round(food['protein_per_100g'] * multiplier, 1),
        'carbs': round(food['carbs_per_100g'] * multiplier, 1),
        'fat': round(food['fat_per_100g'] * multiplier, 1),
        'fiber': round(food['fiber_per_100g'] * multiplier, 1),
        'grams': round(grams, 1),
    }


def calculate_remaining(target: dict, consumed: dict) -> dict:
    """Calculate remaining macros from target - consumed."""
    return {
        'calories': max(0, target['calories_kcal'] - consumed.get('calories', 0)),
        'protein': max(0, target['protein_g'] - consumed.get('protein', 0)),
        'carbs': max(0, target['carbs_g'] - consumed.get('carbs', 0)),
        'fat': max(0, target['fat_g'] - consumed.get('fat', 0)),
        'fiber': max(0, target['fiber_g'] - consumed.get('fiber', 0)),
    }
