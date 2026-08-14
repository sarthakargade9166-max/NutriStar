"""Nutrition calculator — all math is per 100g based with rich micronutrient calculations."""

from typing import Dict, Any
from nutrition.units import convert_to_grams


def calculate_food_nutrition(food: Dict[str, Any], quantity: float, unit: str = 'g') -> Dict[str, Any]:
    """Calculate comprehensive nutrition for a given food, quantity, and unit."""
    effective_unit = unit or food.get('serving_unit') or food.get('servingUnit') or 'g'
    
    if effective_unit in ('g', 'ml'):
        grams = float(quantity)
    else:
        grams = convert_to_grams(float(quantity), effective_unit, food=food)

    multiplier = grams / 100.0

    # Macro values per 100g
    cals_100g = min(max(0.0, float(food.get('calories_per_100g', food.get('caloriesPer100g', 0)))), 900.0)
    p_100g = float(food.get('protein_per_100g', food.get('proteinPer100g', 0)))
    c_100g = float(food.get('carbs_per_100g', food.get('carbsPer100g', 0)))
    f_100g = float(food.get('fat_per_100g', food.get('fatPer100g', 0)))
    fib_100g = float(food.get('fiber_per_100g', food.get('fiberPer100g', 0)))
    sug_100g = float(food.get('sugar_per_100g', food.get('sugarPer100g', 0)))
    sod_100g = float(food.get('sodium_mg_per_100g', food.get('sodiumMgPer100g', 0)))

    res = {
        'calories': round(cals_100g * multiplier, 1),
        'protein': round(p_100g * multiplier, 1),
        'carbs': round(c_100g * multiplier, 1),
        'fat': round(f_100g * multiplier, 1),
        'fiber': round(fib_100g * multiplier, 1),
        'sugar': round(sug_100g * multiplier, 1),
        'sodium': round(sod_100g * multiplier, 1),
        'grams': round(grams, 1),
    }

    if food.get('saturated_fat_per_100g') is not None or food.get('saturatedFatPer100g') is not None:
        sat_100g = float(food.get('saturated_fat_per_100g') if food.get('saturated_fat_per_100g') is not None else food.get('saturatedFatPer100g'))
        res['saturated_fat'] = round(sat_100g * multiplier, 1)

    if food.get('added_sugar_per_100g') is not None or food.get('addedSugarPer100g') is not None:
        add_sug_100g = float(food.get('added_sugar_per_100g') if food.get('added_sugar_per_100g') is not None else food.get('addedSugarPer100g'))
        res['added_sugar'] = round(add_sug_100g * multiplier, 1)

    return res


def calculate_remaining(target: Dict[str, Any], consumed: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate remaining macros from target - consumed."""
    return {
        'calories': max(0, target.get('calories_kcal', target.get('calories', 0)) - consumed.get('calories', 0)),
        'protein': max(0, target.get('protein_g', target.get('protein', 0)) - consumed.get('protein', 0)),
        'carbs': max(0, target.get('carbs_g', target.get('carbs', 0)) - consumed.get('carbs', 0)),
        'fat': max(0, target.get('fat_g', target.get('fat', 0)) - consumed.get('fat', 0)),
        'fiber': max(0, target.get('fiber_g', target.get('fiber', 0)) - consumed.get('fiber', 0)),
    }
