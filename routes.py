"""Routes and request handlers for NutriStar - Login-Free Version with Smart Search."""

import uuid
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
)

routes = Blueprint('routes', __name__)


def get_default_user():
    """
    Retrieves or creates a session-isolated user profile.
    Allows login-free usage while keeping each visitor's logs private on cloud hosts like Render.
    """
    if 'guest_uuid' not in session:
        session['guest_uuid'] = str(uuid.uuid4())

    email = f"{session['guest_uuid']}@guest.nutristar.app"
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(email=email)
        user.set_password('nutristar')
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


# Context Processor: Injects active date, user, and profile into all templates
@routes.app_context_processor
def inject_global_data():
    active_date = session.get('active_date') or get_ist_today()
    user = get_default_user()
    return {
        'active_date': active_date,
        'current_user': user,
        'user_profile': user.profile,
        'ist_today': get_ist_today()
    }


# ==========================================
# MAIN APPLICATION PAGES (LOGIN-FREE)
# ==========================================

@routes.route('/')
def index():
    return redirect(url_for('routes.dashboard'))


@routes.route('/dashboard')
def dashboard():
    user = get_default_user()
    active_date = session.get('active_date') or get_ist_today()

    # Query logged items for active date
    items = MealItem.query.filter_by(user_id=user.id, date=active_date).order_by(MealItem.id.asc()).all()

    # Group items by meal type
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

    # Round totals
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

    quick_add_foods = get_personalized_quick_add(user.id, limit=4)

    # Initial popular staples
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
            name = request.form.get('name', 'User')
            age = int(request.form.get('age', 25))
            gender = request.form.get('gender', 'male')
            height = float(request.form.get('height_cm', 175))
            cur_weight = float(request.form.get('current_weight_kg', 70))
            tgt_weight = float(request.form.get('target_weight_kg', 70))
            activity = request.form.get('activity_level', 'moderate')
            mode = request.form.get('goal_control_mode', 'rate')
            rate = float(request.form.get('target_rate_kg_per_week', 0.5))
            weeks = int(request.form.get('target_weeks', 12))

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
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')

    return render_template('profile.html', profile=user_profile)


@routes.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    user = get_default_user()
    user_profile = user.profile

    if request.method == 'POST':
        try:
            name = request.form.get('name', 'User')
            age = int(request.form.get('age', 25))
            gender = request.form.get('gender', 'male')
            height = float(request.form.get('height_cm', 175))
            cur_weight = float(request.form.get('current_weight_kg', 70))
            tgt_weight = float(request.form.get('target_weight_kg', 70))
            activity = request.form.get('activity_level', 'moderate')
            mode = request.form.get('goal_control_mode', 'rate')
            rate = float(request.form.get('target_rate_kg_per_week', 0.5))

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
        except Exception as e:
            flash(f'Error saving onboarding: {str(e)}', 'error')

    return render_template('onboarding.html', profile=user_profile)


@routes.route('/settings')
def settings():
    user = get_default_user()
    return render_template('settings.html', user=user)


# ==========================================
# DYNAMIC JSON API ENDPOINTS
# ==========================================

@routes.route('/api/foods/search', methods=['GET'])
def api_search_foods():
    raw_q = request.args.get('q', '').strip()
    if not raw_q:
        foods = Food.query.limit(25).all()
        return jsonify([f.to_dict() for f in foods])

    q = raw_q.lower()
    # Normalize plural s/es for queries longer than 3 characters (e.g. chapatis -> chapati, eggs -> egg)
    stems = [q]
    if len(q) > 3 and q.endswith('es'):
        stems.append(q[:-2])
    elif len(q) > 3 and q.endswith('s'):
        stems.append(q[:-1])

    # Load all foods into memory for instantaneous multi-criteria ranking
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
            # 1. Exact match on ID, name or alias
            if term == fid_l or term == name_l or term in aliases_l.split(','):
                score = max(score, 100)
            # 2. Name starts with query
            elif name_l.startswith(term):
                score = max(score, 80)
            # 3. Word in name starts with query
            elif any(w.startswith(term) for w in name_l.split()):
                score = max(score, 70)
            # 4. Word in aliases starts with query
            elif any(w.startswith(term) for a in aliases_l.split(',') for w in a.strip().split()):
                score = max(score, 60)
            # 5. Substring anywhere in name
            elif term in name_l:
                score = max(score, 50)
            # 6. Substring anywhere in aliases or ID
            elif term in aliases_l or term in fid_l:
                score = max(score, 40)
            # 7. Match in Hindi script or category
            elif term in hindi_l or term in cat_l:
                score = max(score, 30)

        if score > 0:
            scored.append((score, food))

    # Sort by score descending, then alphabetical name
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
    unit = data.get('unit', 'serving')

    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'error': 'Not Found', 'message': 'Food not found.'}), 404

    nutrition = calculate_food_nutrition(food, quantity, unit)
    return jsonify(nutrition)


@routes.route('/api/log', methods=['POST'])
def api_log_meal():
    user = get_default_user()
    data = request.get_json() or {}

    food_id = data.get('food_id')
    meal_type = data.get('meal_type', 'lunch').lower()
    quantity = float(data.get('quantity', 1.0))
    unit = data.get('unit', 'serving')
    date_str = data.get('date') or session.get('active_date') or get_ist_today()

    food = db.session.get(Food, food_id)
    if not food:
        return jsonify({'error': 'Not Found', 'message': 'Food item not found.'}), 404

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
        quantity = float(data.get('quantity', item.quantity))
        unit = data.get('unit', item.unit)
        meal_type = data.get('meal_type', item.meal_type).lower()

        food = db.session.get(Food, item.food_id)
        if food:
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
        else:
            return jsonify({'error': 'Error', 'message': 'Food reference not found.'}), 400


@routes.route('/api/active-date', methods=['GET', 'POST'])
def api_active_date():
    if request.method == 'POST':
        data = request.get_json() or {}
        new_date = data.get('date')
        if new_date:
            session['active_date'] = new_date
            return jsonify({'success': True, 'active_date': new_date})
        return jsonify({'error': 'Invalid date'}), 400

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
        cur_weight = float(data.get('weight_kg', 70))
        tgt_weight = float(data.get('target_weight_kg', cur_weight))
        height = float(data.get('height_cm', 175))
        age = int(data.get('age', 25))
        gender = data.get('sex', data.get('gender', 'male'))
        activity = data.get('activity_level', 'moderate')
        mode = data.get('goal_control_mode', 'rate')
        rate = float(data.get('target_rate_kg_per_week', 0.5))
        weeks = int(data.get('target_weeks', 12))

        targets = calculate_targets(cur_weight, tgt_weight, height, age, gender, activity, mode, rate, weeks)
        return jsonify(targets)
    except Exception as e:
        return jsonify({'error': 'Bad Request', 'message': str(e)}), 400


@routes.route('/api/export-data', methods=['GET'])
def api_export_data():
    user = get_default_user()
    items = MealItem.query.filter_by(user_id=user.id).all()

    export_payload = {
        'profile': user.profile.to_dict() if user.profile else None,
        'meal_logs': [item.to_dict() for item in items]
    }
    return jsonify(export_payload)
