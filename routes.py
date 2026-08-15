import uuid
import secrets
import re
from datetime import datetime, timedelta
import pytz
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from database import db
from models import User, Profile, Food, MealItem
from nutrition import (
    calculate_food_nutrition,
    calculate_targets,
    get_personalized_quick_add,
    get_unit_options,
    get_ist_today,
    get_ist_default_meal,
    get_rolling_10_days,
    UNIT_DEFINITIONS,
)
from seed_data import seed_foods_if_empty

routes = Blueprint('routes', __name__)

ALLOWED_MEAL_TYPES = {'breakfast', 'lunch', 'snack', 'dinner'}
ALLOWED_GENDERS = {'male', 'female', 'other'}
ALLOWED_ACTIVITY_LEVELS = {'sedentary', 'light', 'moderate', 'active', 'very_active'}
ALLOWED_GOAL_MODES = {'rate', 'timeline'}


def validate_date_in_rolling_window(date_str):
    if not date_str or not re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_str)):
        return False
    try:
        dt = datetime.strptime(str(date_str), '%Y-%m-%d').date()
        ist = pytz.timezone('Asia/Kolkata')
        today_ist = datetime.now(ist).date()
        oldest_allowed = today_ist - timedelta(days=9)
        return oldest_allowed <= dt <= today_ist
    except ValueError:
        return False


def validate_quantity(qty):
    try:
        val = float(qty)
        return 0.01 <= val <= 1000.0
    except (TypeError, ValueError):
        return False


def validate_unit_for_food(food, unit):
    if not unit or not isinstance(unit, str):
        return False
    u = str(unit).strip().lower()
    if not u or len(u) > 50:
        return False
    valid_options = {opt['value'].lower() for opt in get_unit_options(food)}
    valid_options.update({
        'g', 'grams', 'ml', 'serving', 'piece', 'bowl', 'katori', 'cup', 'glass', 'plate',
        'tablespoon', 'tbsp', 'teaspoon', 'tsp', 'slice', 'pack', 'package',
        str(getattr(food, 'serving_unit', '') or '').lower()
    })
    return u in valid_options


def get_default_user():
    if 'guest_uuid' not in session:
        session['guest_uuid'] = str(uuid.uuid4())

    email = f"{session['guest_uuid']}@guest.nutristar.app"
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(email=email)
        # Generate unpredictable random password hash per guest session
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        db.session.commit()

        profile = Profile(
            user_id=user.id,
            name='User',
            age=25,
            gender='male',
            height_cm=175.0,
            current_weight_kg=70.0,
            target_weight_kg=70.0,
            activity_level='moderate',
            goal_type='maintain',
            goal_control_mode='rate',
            target_rate_kg_per_week=0.5,
            target_weeks=12,
            calorie_target=2000,
            protein_target=120,
            carbs_target=250,
            fat_target=55,
            fiber_target=28
        )
        db.session.add(profile)
        db.session.commit()

    return user


@routes.app_context_processor
def inject_global_data():
    active_date = session.get('active_date') or get_ist_today()
    user = get_default_user()
    return {
        'active_date': active_date,
        'current_user': user,
        'user_profile': user.profile,
        'ist_today': get_ist_today(),
        'csrf_token': session.get('csrf_token', '')
    }


@routes.route('/')
def index():
    return redirect(url_for('routes.dashboard'))


@routes.route('/dashboard')
def dashboard():
    user = get_default_user()
    active_date = session.get('active_date') or get_ist_today()

    items = MealItem.query.filter_by(user_id=user.id, date=active_date).order_by(MealItem.id.asc()).all()

    meals = {'breakfast': [], 'lunch': [], 'snack': [], 'dinner': []}
    totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0, 'fiber': 0.0}

    for item in items:
        mtype = item.meal_type.lower()
        if mtype in meals:
            meals[mtype].append(item)
        totals['calories'] += item.calories
        totals['protein'] += item.protein
        totals['carbs'] += item.carbs
        totals['fat'] += item.fat
        totals['fiber'] += item.fiber

    for k in totals:
        totals[k] = round(totals[k], 1)

    profile = user.profile
    targets = {
        'calories': profile.calorie_target if profile else 2000,
        'protein': profile.protein_target if profile else 120,
        'carbs': profile.carbs_target if profile else 250,
        'fat': profile.fat_target if profile else 55,
        'fiber': profile.fiber_target if profile else 28,
    }

    remaining_calories = max(0, round(targets['calories'] - totals['calories']))

    return render_template(
        'dashboard.html',
        active_date=active_date,
        meals=meals,
        totals=totals,
        targets=targets,
        remaining_calories=remaining_calories,
        ist_today=get_ist_today()
    )


@routes.route('/log-food')
def log_food():
    user = get_default_user()
    active_date = session.get('active_date') or get_ist_today()
    default_meal = request.args.get('meal') or get_ist_default_meal()
    if default_meal not in ALLOWED_MEAL_TYPES:
        default_meal = 'lunch'

    if Food.query.count() == 0:
        seed_foods_if_empty()

    quick_add_foods = get_personalized_quick_add(user.id, limit=4)
    popular_foods = Food.query.limit(25).all()

    return render_template(
        'log_food.html',
        active_date=active_date,
        default_meal=default_meal,
        quick_add_foods=quick_add_foods,
        popular_foods=[f.to_dict() for f in popular_foods]
    )


@routes.route('/history')
def history():
    user = get_default_user()
    rolling_dates = get_rolling_10_days()
    profile = user.profile
    cal_target = profile.calorie_target if profile else 2000

    history_data = []
    for d in rolling_dates:
        date_str = d['date_str']
        items = MealItem.query.filter_by(user_id=user.id, date=date_str).all()
        cal = sum(item.calories for item in items)
        prot = sum(item.protein for item in items)
        carb = sum(item.carbs for item in items)
        fat = sum(item.fat for item in items)

        history_data.append({
            'date_str': date_str,
            'display': d['display'],
            'day_name': d['day_name'],
            'is_today': d['is_today'],
            'item_count': len(items),
            'calories': round(cal, 1),
            'protein': round(prot, 1),
            'carbs': round(carb, 1),
            'fat': round(fat, 1),
            'target': cal_target,
            'pct': min(100, round((cal / cal_target) * 100)) if cal_target > 0 else 0
        })

    return render_template('history.html', history_data=history_data)


@routes.route('/history/<date_str>')
def history_day(date_str):
    if not validate_date_in_rolling_window(date_str):
        flash('Requested date is outside the allowable 10-day history window.', 'error')
        return redirect(url_for('routes.history'))

    user = get_default_user()
    session['active_date'] = date_str

    items = MealItem.query.filter_by(user_id=user.id, date=date_str).order_by(MealItem.id.asc()).all()
    meals = {'breakfast': [], 'lunch': [], 'snack': [], 'dinner': []}
    totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0, 'fiber': 0.0}

    for item in items:
        mtype = item.meal_type.lower()
        if mtype in meals:
            meals[mtype].append(item)
        totals['calories'] += item.calories
        totals['protein'] += item.protein
        totals['carbs'] += item.carbs
        totals['fat'] += item.fat
        totals['fiber'] += item.fiber

    profile = user.profile
    targets = {
        'calories': profile.calorie_target if profile else 2000,
        'protein': profile.protein_target if profile else 120,
        'carbs': profile.carbs_target if profile else 250,
        'fat': profile.fat_target if profile else 55,
    }

    return render_template(
        'history_day.html',
        date_str=date_str,
        meals=meals,
        totals=totals,
        targets=targets
    )


@routes.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_default_user()
    user_profile = user.profile

    if request.method == 'POST':
        try:
            name = (request.form.get('name') or 'User').strip()[:50]
            age = max(10, min(120, int(request.form.get('age', 25))))
            gender = request.form.get('gender', 'male').lower()
            if gender not in ALLOWED_GENDERS:
                gender = 'male'

            height = max(50.0, min(250.0, float(request.form.get('height_cm', 175))))
            cur_weight = max(20.0, min(300.0, float(request.form.get('current_weight_kg', 70))))
            tgt_weight = max(20.0, min(300.0, float(request.form.get('target_weight_kg', 70))))

            activity = request.form.get('activity_level', 'moderate').lower()
            if activity not in ALLOWED_ACTIVITY_LEVELS:
                activity = 'moderate'

            mode = request.form.get('goal_control_mode', 'rate').lower()
            if mode not in ALLOWED_GOAL_MODES:
                mode = 'rate'

            rate = max(0.1, min(1.5, float(request.form.get('target_rate_kg_per_week', 0.5))))
            weeks = max(1, min(52, int(request.form.get('target_weeks', 12))))

            targets = calculate_targets(
                cur_weight, tgt_weight, height, age, gender, activity,
                goal_control_mode=mode, target_rate_kg_per_week=rate, target_weeks=weeks
            )

            user_profile.name = name
            user_profile.age = age
            user_profile.gender = gender
            user_profile.height_cm = height
            user_profile.current_weight_kg = cur_weight
            user_profile.target_weight_kg = tgt_weight
            user_profile.activity_level = activity
            user_profile.goal_type = targets['goal_type']
            user_profile.goal_control_mode = mode
            user_profile.target_rate_kg_per_week = rate
            user_profile.target_weeks = weeks
            user_profile.calorie_target = targets['calories']
            user_profile.protein_target = targets['protein']
            user_profile.carbs_target = targets['carbs']
            user_profile.fat_target = targets['fat']
            user_profile.fiber_target = targets['fiber']

            db.session.commit()
            flash('Profile and nutrition targets updated successfully.', 'success')
        except (ValueError, TypeError):
            flash('Invalid input values. Please review your entries.', 'error')

    return render_template('profile.html', profile=user_profile)


@routes.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    user = get_default_user()
    user_profile = user.profile

    if request.method == 'POST':
        try:
            name = (request.form.get('name') or 'User').strip()[:50]
            age = max(10, min(120, int(request.form.get('age', 25))))
            gender = request.form.get('gender', 'male').lower()
            if gender not in ALLOWED_GENDERS:
                gender = 'male'

            height = max(50.0, min(250.0, float(request.form.get('height_cm', 175))))
            cur_weight = max(20.0, min(300.0, float(request.form.get('current_weight_kg', 70))))
            tgt_weight = max(20.0, min(300.0, float(request.form.get('target_weight_kg', 70))))

            activity = request.form.get('activity_level', 'moderate').lower()
            if activity not in ALLOWED_ACTIVITY_LEVELS:
                activity = 'moderate'

            mode = request.form.get('goal_control_mode', 'rate').lower()
            if mode not in ALLOWED_GOAL_MODES:
                mode = 'rate'

            rate = max(0.1, min(1.5, float(request.form.get('target_rate_kg_per_week', 0.5))))

            targets = calculate_targets(cur_weight, tgt_weight, height, age, gender, activity, mode, rate)

            user_profile.name = name
            user_profile.age = age
            user_profile.gender = gender
            user_profile.height_cm = height
            user_profile.current_weight_kg = cur_weight
            user_profile.target_weight_kg = tgt_weight
            user_profile.activity_level = activity
            user_profile.goal_type = targets['goal_type']
            user_profile.calorie_target = targets['calories']
            user_profile.protein_target = targets['protein']
            user_profile.carbs_target = targets['carbs']
            user_profile.fat_target = targets['fat']
            user_profile.fiber_target = targets['fiber']

            db.session.commit()
            return redirect(url_for('routes.dashboard'))
        except (ValueError, TypeError):
            flash('Invalid input values. Please review your entries.', 'error')

    return render_template('onboarding.html', profile=user_profile)


@routes.route('/settings')
def settings():
    user = get_default_user()
    return render_template('settings.html', user=user)


@routes.route('/api/foods/search', methods=['GET'])
def api_search_foods():
    if Food.query.count() == 0:
        seed_foods_if_empty()

    raw_q = request.args.get('q', '').strip()
    if not raw_q:
        foods = Food.query.limit(25).all()
        return jsonify([f.to_dict() for f in foods])

    q = raw_q.lower()
    stems = [q]
    if len(q) > 3 and q.endswith('es'):
        stems.append(q[:-2])
    elif len(q) > 3 and q.endswith('s'):
        stems.append(q[:-1])

    all_foods = Food.query.all()
    scored = []

    for food in all_foods:
        name_l = food.name.lower()
        hindi_l = (food.hindi_name or '').lower()
        aliases_l = (food.aliases or '').lower()
        cat_l = (food.category or '').lower()
        fid_l = food.id.lower()

        score = 0
        for term in stems:
            if term == fid_l or term == name_l or term in aliases_l.split(','):
                score = max(score, 100)
            elif name_l.startswith(term):
                score = max(score, 80)
            elif any(w.startswith(term) for w in name_l.split()):
                score = max(score, 70)
            elif any(w.startswith(term) for a in aliases_l.split(',') for w in a.strip().split()):
                score = max(score, 60)
            elif term in name_l:
                score = max(score, 50)
            elif term in aliases_l or term in fid_l:
                score = max(score, 40)
            elif term in hindi_l or term in cat_l:
                score = max(score, 30)

        if score > 0:
            scored.append((score, food))

    scored.sort(key=lambda x: (-x[0], x[1].name))
    results = [item[1].to_dict() for item in scored[:35]]

    return jsonify(results)


@routes.route('/api/foods/<food_id>', methods=['GET'])
def api_get_food(food_id):
    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'error': 'Not Found', 'message': 'Food not found.'}), 404

    food_dict = food.to_dict()
    food_dict['unit_options'] = get_unit_options(food)
    return jsonify(food_dict)


@routes.route('/api/calculate', methods=['POST'])
def api_calculate():
    data = request.get_json() or {}
    food_id = data.get('food_id')
    quantity = data.get('quantity', 1.0)
    unit = str(data.get('unit', 'serving')).strip()

    if not validate_quantity(quantity):
        return jsonify({'error': 'Bad Request', 'message': 'Invalid portion quantity.'}), 400

    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'error': 'Not Found', 'message': 'Food not found.'}), 404

    if not validate_unit_for_food(food, unit):
        return jsonify({'error': 'Bad Request', 'message': f'Unsupported serving unit for {food.name}.'}), 400

    nutrition = calculate_food_nutrition(food, float(quantity), unit)
    return jsonify(nutrition)


@routes.route('/api/log', methods=['POST'])
def api_log_meal():
    user = get_default_user()
    data = request.get_json() or {}

    food_id = data.get('food_id')
    meal_type = str(data.get('meal_type', 'lunch')).lower()
    quantity_raw = data.get('quantity', 1.0)
    unit = str(data.get('unit', 'serving')).strip()
    date_str = data.get('date') or session.get('active_date') or get_ist_today()

    if meal_type not in ALLOWED_MEAL_TYPES:
        return jsonify({'error': 'Bad Request', 'message': 'Invalid meal category.'}), 400

    if not validate_quantity(quantity_raw):
        return jsonify({'error': 'Bad Request', 'message': 'Invalid quantity. Must be between 0.01 and 1000.'}), 400

    if not validate_date_in_rolling_window(date_str):
        return jsonify({'error': 'Bad Request', 'message': 'Date must be within the allowable 10-day rolling window.'}), 400

    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'error': 'Not Found', 'message': 'Food item not found.'}), 404

    if not validate_unit_for_food(food, unit):
        return jsonify({'error': 'Bad Request', 'message': f'Unsupported serving unit for {food.name}.'}), 400

    quantity = float(quantity_raw)
    nutrition = calculate_food_nutrition(food, quantity, unit)

    item = MealItem(
        user_id=user.id,
        date=date_str,
        meal_type=meal_type,
        food_id=food.id,
        food_name=food.name,
        quantity=quantity,
        unit=unit,
        grams=nutrition['grams'],
        calories=nutrition['calories'],
        protein=nutrition['protein'],
        carbs=nutrition['carbs'],
        fat=nutrition['fat'],
        fiber=nutrition['fiber']
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'success': True, 'item': item.to_dict()}), 201


@routes.route('/api/meal-items/<int:item_id>', methods=['PUT', 'DELETE'])
def api_manage_meal_item(item_id):
    user = get_default_user()
    item = MealItem.query.filter_by(id=item_id, user_id=user.id).first()

    if not item:
        return jsonify({'error': 'Not Found', 'message': 'Meal item not found.'}), 404

    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Meal item deleted.'})

    if request.method == 'PUT':
        data = request.get_json() or {}
        quantity_raw = data.get('quantity', item.quantity)
        unit = str(data.get('unit', item.unit)).strip()
        meal_type = str(data.get('meal_type', item.meal_type)).lower()

        if meal_type not in ALLOWED_MEAL_TYPES:
            return jsonify({'error': 'Bad Request', 'message': 'Invalid meal category.'}), 400

        if not validate_quantity(quantity_raw):
            return jsonify({'error': 'Bad Request', 'message': 'Invalid quantity.'}), 400

        food = db.session.get(Food, item.food_id)
        if not food:
            return jsonify({'error': 'Error', 'message': 'Food reference not found.'}), 400

        if not validate_unit_for_food(food, unit):
            return jsonify({'error': 'Bad Request', 'message': f'Unsupported serving unit for {food.name}.'}), 400

        quantity = float(quantity_raw)
        nutrition = calculate_food_nutrition(food, quantity, unit)
        item.quantity = quantity
        item.unit = unit
        item.meal_type = meal_type
        item.grams = nutrition['grams']
        item.calories = nutrition['calories']
        item.protein = nutrition['protein']
        item.carbs = nutrition['carbs']
        item.fat = nutrition['fat']
        item.fiber = nutrition['fiber']
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})


@routes.route('/api/active-date', methods=['GET', 'POST'])
def api_active_date():
    if request.method == 'POST':
        data = request.get_json() or {}
        new_date = str(data.get('date', '')).strip()
        if validate_date_in_rolling_window(new_date):
            session['active_date'] = new_date
            return jsonify({'success': True, 'active_date': new_date})
        return jsonify({'error': 'Bad Request', 'message': 'Date must be within the allowable 10-day rolling window.'}), 400

    return jsonify({'active_date': session.get('active_date') or get_ist_today()})


@routes.route('/api/quick-add', methods=['GET'])
def api_quick_add():
    user = get_default_user()
    foods = get_personalized_quick_add(user.id, limit=4)
    return jsonify(foods)


@routes.route('/api/targets', methods=['POST'])
def api_targets():
    data = request.get_json() or {}
    try:
        cur_weight = max(20.0, min(300.0, float(data.get('weight_kg', 70))))
        tgt_weight = max(20.0, min(300.0, float(data.get('target_weight_kg', cur_weight))))
        height = max(50.0, min(250.0, float(data.get('height_cm', 175))))
        age = max(10, min(120, int(data.get('age', 25))))
        gender = str(data.get('sex', data.get('gender', 'male'))).lower()
        if gender not in ALLOWED_GENDERS:
            gender = 'male'

        activity = str(data.get('activity_level', 'moderate')).lower()
        if activity not in ALLOWED_ACTIVITY_LEVELS:
            activity = 'moderate'

        mode = str(data.get('goal_control_mode', 'rate')).lower()
        if mode not in ALLOWED_GOAL_MODES:
            mode = 'rate'

        rate = max(0.1, min(1.5, float(data.get('target_rate_kg_per_week', 0.5))))
        weeks = max(1, min(52, int(data.get('target_weeks', 12))))

        targets = calculate_targets(cur_weight, tgt_weight, height, age, gender, activity, mode, rate, weeks)
        return jsonify(targets)
    except (ValueError, TypeError):
        return jsonify({'error': 'Bad Request', 'message': 'Invalid input parameters.'}), 400


@routes.route('/api/export-data', methods=['GET'])
def api_export_data():
    user = get_default_user()
    items = MealItem.query.filter_by(user_id=user.id).all()

    export_payload = {
        'profile': user.profile.to_dict() if user.profile else None,
        'meal_logs': [item.to_dict() for item in items]
    }
    return jsonify(export_payload)
