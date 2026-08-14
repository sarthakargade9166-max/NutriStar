"""Unit conversion — household Indian units to grams."""

UNIT_GRAMS = {
    'g': 1,
    'gram': 1,
    'grams': 1,
    'kg': 1000,
    'ml': 1,
    'l': 1000,
    'liter': 1000,
    'piece': 50,
    'bowl': 150,
    'katori': 150,
    'cup': 240,
    'glass': 250,
    'tablespoon': 15,
    'tbsp': 15,
    'teaspoon': 5,
    'tsp': 5,
    'plate': 300,
    'serving': 150,
    'slice': 30,
}


def convert_to_grams(quantity: float, unit: str, food_name: str = '') -> float:
    """Convert a quantity + unit to grams."""
    lower = unit.lower().strip()
    factor = UNIT_GRAMS.get(lower, 100)
    return quantity * factor
