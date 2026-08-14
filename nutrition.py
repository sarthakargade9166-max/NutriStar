"""Nutrition calculation and serving size logic for NutriStar."""

from datetime import datetime, timedelta, timezone
import pytz
from database import db

# Unit definitions and reference gram weights
UNIT_DEFINITIONS = {
    'piece': {'label': 'Piece', 'default_grams': 50.0},
    'bowl': {'label': 'Bowl (Katori)', 'default_grams': 150.0},
    'katori': {'label': 'Bowl (Katori)', 'default_grams': 150.0},
    'glass': {'label': 'Glass', 'default_grams': 250.0},
    'cup': {'label': 'Cup', 'default_grams': 120.0},
    'plate': {'label': 'Plate', 'default_grams': 300.0},
    'serving': {'label': 'Serving', 'default_grams': 150.0},
    'slice': {'label': 'Slice', 'default_grams': 30.0},
    'tablespoon': {'label': 'Tablespoon (tbsp)', 'default_grams': 15.0},
    'tbsp': {'label': 'Tablespoon (tbsp)', 'default_grams': 15.0},
    'teaspoon': {'label': 'Teaspoon (tsp)', 'default_grams': 5.0},
    'tsp': {'label': 'Teaspoon (tsp)', 'default_grams': 5.0},
    'g': {'label': 'Grams (g)', 'default_grams': 1.0},
    'grams': {'label': 'Grams (g)', 'default_grams': 1.0},
    'ml': {'label': 'Milliliters (ml)', 'default_grams': 1.0},
}


def get_unit_options(food):
    """Returns available serving units for a given food."""
    unit = (food.get('serving_unit') or getattr(food, 'serving_unit', 'serving')).lower()
    category = (food.get('category') or getattr(food, 'category', '')).lower()
    name = (food.get('name') or getattr(food, 'name', '')).lower()

    options = []

    if category == 'beverages' or unit == 'ml' or 'tea' in name or 'coffee' in name or 'juice' in name or 'milk' in name or 'lassi' in name or 'chaas' in name:
        options = [
            {'value': 'ml', 'label': 'Milliliters (ml)'},
            {'value': 'cup', 'label': 'Cup (200 ml)'},
            {'value': 'glass', 'label': 'Glass (250 ml)'},
        ]
    elif unit == 'piece' or 'roti' in name or 'chapati' in name or 'bhakri' in name or 'egg' in name or 'idli' in name or 'samosa' in name or 'vada' in name or 'banana' in name or 'apple' in name:
        options = [
            {'value': 'piece', 'label': 'Piece'},
            {'value': 'g', 'label': 'Grams (g)'},
        ]
    elif unit in ['bowl', 'katori'] or category in ['rice', 'dals', 'vegetables'] or 'dal' in name or 'curry' in name or 'khichdi' in name or 'poha' in name or 'sabji' in name or 'bhaji' in name or 'rice' in name:
        options = [
            {'value': 'bowl', 'label': 'Bowl (Katori - 150g)'},
            {'value': 'cup', 'label': 'Cup (120g)'},
            {'value': 'plate', 'label': 'Plate (300g)'},
            {'value': 'g', 'label': 'Grams (g)'},
        ]
    elif unit in ['tablespoon', 'tbsp', 'teaspoon', 'tsp'] or 'ghee' in name or 'oil' in name or 'butter' in name or 'chutney' in name:
        options = [
            {'value': 'tablespoon', 'label': 'Tablespoon (15g)'},
            {'value': 'teaspoon', 'label': 'Teaspoon (5g)'},
            {'value': 'g', 'label': 'Grams (g)'},
        ]
    else:
        options = [
            {'value': 'serving', 'label': f"Serving ({int(food.get('grams_per_serving', 100) if isinstance(food, dict) else getattr(food, 'grams_per_serving', 100))}g)"},
            {'value': 'g', 'label': 'Grams (g)'},
        ]

    return options


def calculate_food_nutrition(food, quantity, unit):
    """Calculates calories and macronutrients for a given food and serving."""
    try:
        qty = float(quantity)
        if qty <= 0:
            qty = 1.0
    except (ValueError, TypeError):
        qty = 1.0

    unit_norm = (unit or 'serving').lower()

    # Get food attributes (handles both dict and SQLAlchemy Model)
    grams_per_serving = float(food.get('grams_per_serving', 100.0) if isinstance(food, dict) else getattr(food, 'grams_per_serving', 100.0) or 100.0)
    cal_100g = float(food.get('calories_100g', 0.0) if isinstance(food, dict) else getattr(food, 'calories_100g', 0.0) or 0.0)
    prot_100g = float(food.get('protein_100g', 0.0) if isinstance(food, dict) else getattr(food, 'protein_100g', 0.0) or 0.0)
    carb_100g = float(food.get('carbs_100g', 0.0) if isinstance(food, dict) else getattr(food, 'carbs_100g', 0.0) or 0.0)
    fat_100g = float(food.get('fat_100g', 0.0) if isinstance(food, dict) else getattr(food, 'fat_100g', 0.0) or 0.0)
    fiber_100g = float(food.get('fiber_100g', 0.0) if isinstance(food, dict) else getattr(food, 'fiber_100g', 0.0) or 0.0)

    # Determine total grams
    if unit_norm in ['g', 'grams', 'ml']:
        total_grams = qty
    elif unit_norm in ['serving', 'package']:
        total_grams = qty * grams_per_serving
    elif unit_norm == 'piece':
        total_grams = qty * grams_per_serving
    elif unit_norm in ['bowl', 'katori']:
        total_grams = qty * 150.0
    elif unit_norm == 'glass':
        total_grams = qty * 250.0
    elif unit_norm == 'cup':
        total_grams = qty * 120.0 if 'rice' in (food.get('name', '') if isinstance(food, dict) else getattr(food, 'name', '')).lower() else qty * 200.0
    elif unit_norm == 'plate':
        total_grams = qty * 300.0
    elif unit_norm in ['tablespoon', 'tbsp']:
        total_grams = qty * 15.0
    elif unit_norm in ['teaspoon', 'tsp']:
        total_grams = qty * 5.0
    else:
        total_grams = qty * grams_per_serving

    factor = total_grams / 100.0

    return {
        'grams': round(total_grams, 1),
        'calories': round(cal_100g * factor, 1),
        'protein': round(prot_100g * factor, 1),
        'carbs': round(carb_100g * factor, 1),
        'fat': round(fat_100g * factor, 1),
        'fiber': round(fiber_100g * factor, 1)
    }


def calculate_tdee(weight_kg, height_cm, age, gender, activity_level):
    """Calculates BMR and TDEE using the Mifflin-St Jeor equation."""
    if gender.lower() == 'female':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5

    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'very_active': 1.725,
        'extra_active': 1.9
    }
    multiplier = multipliers.get(activity_level.lower(), 1.55)
    return round(bmr * multiplier)


def calculate_targets(current_weight, target_weight, height_cm, age, gender, activity_level,
                      goal_control_mode='rate', target_rate_kg_per_week=0.5, target_weeks=12):
    """Calculates daily calorie and macronutrient targets based on weight goals."""
    tdee = calculate_tdee(current_weight, height_cm, age, gender, activity_level)
    diff = target_weight - current_weight

    if abs(diff) < 0.2:
        goal_type = 'maintain'
        target_calories = tdee
    elif diff < 0:
        goal_type = 'lose'
        if goal_control_mode == 'rate':
            rate = min(max(target_rate_kg_per_week, 0.1), 1.5)
            deficit = (rate * 7700) / 7
            target_calories = max(1200 if gender == 'female' else 1500, round(tdee - deficit))
        else:
            weeks = max(target_weeks, 1)
            total_deficit = abs(diff) * 7700
            daily_deficit = total_deficit / (weeks * 7)
            target_calories = max(1200 if gender == 'female' else 1500, round(tdee - daily_deficit))
    else:
        goal_type = 'gain'
        if goal_control_mode == 'rate':
            rate = min(max(target_rate_kg_per_week, 0.1), 1.0)
            surplus = (rate * 7700) / 7
            target_calories = round(tdee + surplus)
        else:
            weeks = max(target_weeks, 1)
            total_surplus = abs(diff) * 7700
            daily_surplus = total_surplus / (weeks * 7)
            target_calories = round(tdee + daily_surplus)

    # Macronutrient distribution
    protein_multiplier = 1.8 if goal_type == 'lose' else (1.6 if goal_type == 'gain' else 1.4)
    protein_g = round(current_weight * protein_multiplier)
    protein_cals = protein_g * 4

    fat_cals = target_calories * 0.25
    fat_g = round(fat_cals / 9)
    actual_fat_cals = fat_g * 9

    carb_cals = max(0, target_calories - protein_cals - actual_fat_cals)
    carbs_g = round(carb_cals / 4)

    fiber_g = round((target_calories / 1000) * 14)

    return {
        'tdee': tdee,
        'goal_type': goal_type,
        'calories': target_calories,
        'protein': protein_g,
        'carbs': carbs_g,
        'fat': fat_g,
        'fiber': fiber_g
    }


def get_personalized_quick_add(user_id, limit=4):
    """
    Ranks foods logged by the user in the last 10 days by frequency (primary)
    and recency (secondary). Falls back to standard staples if logs < limit.
    """
    from models import MealItem, Food

    ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=10)).strftime('%Y-%m-%d')
    recent_items = MealItem.query.filter(
        MealItem.user_id == user_id,
        MealItem.date >= ten_days_ago
    ).all()

    food_counts = {}
    last_logged = {}

    for item in recent_items:
        fid = item.food_id
        food_counts[fid] = food_counts.get(fid, 0) + 1
        item_created = item.created_at or datetime.min.replace(tzinfo=timezone.utc)
        if fid not in last_logged or item_created > last_logged[fid]:
            last_logged[fid] = item_created

    # Sort by frequency desc, recency desc
    min_date = datetime.min.replace(tzinfo=timezone.utc)
    sorted_fids = sorted(
        food_counts.keys(),
        key=lambda fid: (food_counts[fid], last_logged.get(fid, min_date)),
        reverse=True
    )

    result_foods = []
    seen = set()

    for fid in sorted_fids:
        food = db.session.get(Food, fid)
        if food and food.id not in seen:
            result_foods.append(food)
            seen.add(food.id)
            if len(result_foods) >= limit:
                break

    # Fallback staples if user has fewer than limit
    if len(result_foods) < limit:
        staple_ids = ['chapati', 'rice-cooked', 'chai', 'filter-coffee', 'toor-dal-cooked', 'boiled-egg']
        for sid in staple_ids:
            if sid not in seen:
                food = db.session.get(Food, sid)
                if food:
                    result_foods.append(food)
                    seen.add(food.id)
                    if len(result_foods) >= limit:
                        break

    return [f.to_dict() for f in result_foods]


def get_ist_today():
    """Returns today's date string (YYYY-MM-DD) in Indian Standard Time."""
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime('%Y-%m-%d')


def get_ist_default_meal():
    """Returns default meal type (breakfast, lunch, snack, dinner) based on IST time."""
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    hour = now.hour

    if 4 <= hour < 12:
        return 'breakfast'
    elif 12 <= hour < 16:
        return 'lunch'
    elif 16 <= hour < 18:
        return 'snack'
    else:
        return 'dinner'


def get_rolling_10_days():
    """Returns list of last 10 dates (today + previous 9 days) with display formatting."""
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    dates = []
    for i in range(10):
        d = now - timedelta(days=i)
        dates.append({
            'date_str': d.strftime('%Y-%m-%d'),
            'display': d.strftime('%d %b %Y'),
            'day_name': d.strftime('%a'),
            'is_today': (i == 0)
        })
    return dates
