from dataclasses import dataclass, field
from typing import Optional

# ===== Food Types =====

FOOD_CATEGORIES = [
    'cereals', 'breads', 'rice', 'dals', 'vegetables', 'dairy',
    'eggs_meat', 'snacks_fried', 'snacks_healthy', 'south_indian',
    'sweets', 'beverages', 'fruits', 'prepared', 'packaged', 'condiments'
]

CATEGORY_LABELS = {
    'cereals': 'Cereals & Grains', 'breads': 'Rotis & Breads',
    'rice': 'Rice Dishes', 'dals': 'Dals & Legumes',
    'vegetables': 'Vegetables', 'dairy': 'Paneer & Dairy',
    'eggs_meat': 'Eggs & Meat', 'snacks_fried': 'Fried Snacks',
    'snacks_healthy': 'Healthy Snacks', 'south_indian': 'South Indian',
    'sweets': 'Sweets', 'beverages': 'Beverages',
    'fruits': 'Fruits', 'prepared': 'Prepared Dishes',
    'packaged': 'Packaged Foods', 'condiments': 'Condiments & Oils',
}

ACTIVITY_LABELS = {
    'sedentary': 'Sedentary (little/no exercise)',
    'light': 'Light (1-3 days/week)',
    'moderate': 'Moderate (3-5 days/week)',
    'active': 'Active (6-7 days/week)',
    'very_active': 'Very Active (twice/day)',
}

GOAL_LABELS = {
    'lose': 'Lose Weight',
    'maintain': 'Maintain Weight',
    'gain': 'Gain Weight',
    'muscle': 'Build Muscle',
}

MEAL_LABELS = {
    'breakfast': 'Breakfast',
    'lunch': 'Lunch',
    'snack': 'Snack',
    'dinner': 'Dinner',
}

DIETARY_LABELS = {
    'vegetarian': 'Vegetarian',
    'vegan': 'Vegan',
    'eggetarian': 'Eggetarian',
    'non_vegetarian': 'Non-Vegetarian',
    'any': 'Any',
}
