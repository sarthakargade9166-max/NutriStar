"""JSON API routes — with strict input validation & defensive security."""

from flask import Blueprint, request, jsonify, current_app
from nutrition.targets import calculate_targets
from nutrition.calculator import calculate_food_nutrition

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/foods', methods=['GET'])
def get_all_foods():
    """Return full food database as JSON with optional category filter."""
    from data.foods import FOODS
    category = request.args.get('category', '').strip()[:50]
    if category:
        filtered = [f for f in FOODS if f.get('category') == category]
        return jsonify(filtered)
    return jsonify(FOODS)


@api.route('/foods/search', methods=['GET'])
def search_foods_route():
    """Search foods by query string and optional category with input sanitization."""
    from data.foods import search_foods
    q = request.args.get('q', '').strip()[:100]  # Bound query string length
    category = request.args.get('category', '').strip()[:50] or None
    results = search_foods(query=q, category=category)
    return jsonify(results)


@api.route('/foods/<food_id>', methods=['GET'])
def get_food(food_id):
    """Get single food by ID with sanitized lookup."""
    from data.foods import get_food_by_id
    sanitized_id = (food_id or '').strip()[:100]
    food = get_food_by_id(sanitized_id)
    if food:
        return jsonify(food)
    return jsonify({'error': 'Food not found'}), 404


@api.route('/targets', methods=['POST'])
def calc_targets():
    """Calculate daily nutrition targets from profile with strict boundary validation."""
    profile = request.get_json(silent=True)
    if not isinstance(profile, dict):
        return jsonify({'error': 'Invalid JSON payload'}), 400

    try:
        raw_weight = float(profile.get('weight_kg') or profile.get('weight') or 70)
        raw_height = float(profile.get('height_cm') or profile.get('height') or 170)
        raw_age = int(profile.get('age') or 25)

        # Enforce realistic physiological bounds (Defends against logic manipulation / overflows)
        weight_kg = max(20.0, min(raw_weight, 500.0))
        height_cm = max(50.0, min(raw_height, 300.0))
        age = max(5, min(raw_age, 120))

        raw_sex = str(profile.get('sex') or 'male').lower()
        sex = raw_sex if raw_sex in ('male', 'female') else 'male'

        raw_activity = str(profile.get('activity_level') or profile.get('activity') or 'sedentary').lower()
        valid_activities = ('sedentary', 'light', 'moderate', 'active', 'very_active')
        activity_level = raw_activity if raw_activity in valid_activities else 'sedentary'

        raw_goal = str(profile.get('goal') or 'maintain').lower()
        valid_goals = ('lose', 'maintain', 'gain', 'muscle')
        goal = raw_goal if raw_goal in valid_goals else 'maintain'

        norm_profile = {
            'weight_kg': weight_kg,
            'height_cm': height_cm,
            'age': age,
            'sex': sex,
            'activity_level': activity_level,
            'goal': goal,
        }

        targets = calculate_targets(norm_profile)
        targets['calories'] = targets['calories_kcal']
        targets['protein'] = targets['protein_g']
        targets['carbs'] = targets['carbs_g']
        targets['fat'] = targets['fat_g']
        targets['fiber'] = targets['fiber_g']
        return jsonify(targets)
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid numerical values for profile metrics'}), 400


@api.route('/nutrition/calculate', methods=['POST'])
def calc_nutrition():
    """Calculate nutrition for a food + quantity + unit with strict non-negative validation."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON payload'}), 400

    from data.foods import get_food_by_id
    food_id = str(data.get('food_id', ''))[:100]
    food = get_food_by_id(food_id)
    if not food:
        return jsonify({'error': 'Food not found'}), 404

    try:
        raw_quantity = float(data.get('quantity', 1))
        # Prevent negative quantities / zero / absurd numbers (Business Logic Integrity)
        if raw_quantity <= 0 or raw_quantity > 10000:
            return jsonify({'error': 'Quantity must be positive and below 10,000'}), 400
        quantity = raw_quantity
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity number'}), 400

    unit = str(data.get('unit', food.get('serving_unit', 'g')))[:20]
    result = calculate_food_nutrition(food, quantity, unit)
    return jsonify(result)


@api.route('/ai/parse-food', methods=['POST'])
def parse_food():
    """Parse natural language food input via Gemini with input bounds."""
    data = request.get_json(silent=True) or {}
    input_text = str(data.get('input', '') or data.get('text', '')).strip()[:1000]
    api_key = str(data.get('api_key', '')).strip() or current_app.config.get('GEMINI_API_KEY', '')

    if not input_text:
        return jsonify({'error': 'Input text required'}), 400
    if not api_key:
        from data.foods import search_foods
        words = input_text.lower().split()
        matched_foods = []
        for word in words:
            if len(word) > 2:
                found = search_foods(word, limit=1)
                if found and found[0] not in matched_foods:
                    matched_foods.append({
                        'name': found[0]['name'],
                        'quantity': 1,
                        'unit': found[0]['serving_unit']
                    })
        return jsonify({
            'meal_type': 'lunch' if 'lunch' in input_text.lower() else 'dinner' if 'dinner' in input_text.lower() else 'breakfast' if 'breakfast' in input_text.lower() else 'snack',
            'foods': matched_foods
        })

    from ai.food_parser import parse_food_input
    result = parse_food_input(input_text, api_key)
    return jsonify(result)


@api.route('/ai/analyze', methods=['POST'])
def analyze():
    """Analyze diet via Gemini with structured fallback."""
    data = request.get_json(silent=True) or {}
    context = data.get('context', {})
    if not context:
        context = {
            'profile': data.get('profile', {}),
            'logs': data.get('logs', {}),
        }
    api_key = str(data.get('api_key', '')).strip() or current_app.config.get('GEMINI_API_KEY', '')

    if not api_key:
        profile = context.get('profile', {}) if isinstance(context.get('profile'), dict) else {}
        logs = context.get('logs', {}) if isinstance(context.get('logs'), dict) else {}
        total_p = 0

        for date_str, meal_dict in logs.items():
            if isinstance(meal_dict, dict):
                for meal_name, items in meal_dict.items():
                    if isinstance(items, list):
                        for itm in items:
                            if isinstance(itm, dict):
                                total_p += float(itm.get('protein', 0) or 0)

        return jsonify({
            'summary': f"Diet analysis based on logged meals. Maintain consistency to meet your {profile.get('goal', 'health')} goals.",
            'priority': 'protein' if total_p < 50 else 'balanced',
            'tips': [
                "Include a clean protein source like Paneer, Soya chunks, Moong dal, Sprouts, or Boiled Eggs with each main meal.",
                "Opt for whole grain breads (Jowar, Bajra, or Whole Wheat Roti) to support steady blood glucose and digestion.",
                "Ensure adequate hydration of 2.5-3 liters daily."
            ],
            'recommendations': [
                {'food': 'Soya Chunks', 'name': 'Soya Chunks (Nutrela)', 'quantity': '1 cup (50g)', 'reason': '52g protein per 100g with low fat'},
                {'food': 'Paneer / Tofu', 'name': 'Paneer / Tofu', 'quantity': '100g', 'reason': 'Rich source of bioavailable protein and calcium'},
                {'food': 'Moong Sprouts', 'name': 'Sprouted Moong Salad', 'quantity': '1 bowl (100g)', 'reason': 'High fiber, micronutrient-dense plant protein'}
            ]
        })

    from ai.diet_analyst import analyze_diet
    result = analyze_diet(context, api_key)
    return jsonify(result)
