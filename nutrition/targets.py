"""BMR/TDEE target calculator using Mifflin-St Jeor equation."""


ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}


def calculate_targets(profile: dict) -> dict:
    """Calculate daily nutrition targets from user profile."""
    weight = profile['weight_kg']
    height = profile['height_cm']
    age = profile['age']
    sex = profile['sex']
    activity = profile['activity_level']
    goal = profile['goal']

    # Mifflin-St Jeor
    bmr = 10 * weight + 6.25 * height - 5 * age
    bmr += 5 if sex == 'male' else -161

    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity, 1.2)

    # Adjust for goal
    target_calories = tdee
    protein_multiplier = 1.0

    if goal == 'lose':
        target_calories -= 500
        protein_multiplier = 1.2
    elif goal == 'gain':
        target_calories += 300
        protein_multiplier = 1.2
    elif goal == 'muscle':
        target_calories += 200
        protein_multiplier = 1.6

    # Floor
    min_cal = 1500 if sex == 'male' else 1200
    target_calories = max(target_calories, min_cal)

    protein_g = weight * protein_multiplier
    fat_calories = target_calories * 0.25
    fat_g = fat_calories / 9
    protein_calories = protein_g * 4
    carb_calories = target_calories - protein_calories - fat_calories
    carbs_g = carb_calories / 4
    fiber_g = (target_calories / 1000) * 14

    return {
        'calories_kcal': round(target_calories),
        'protein_g': round(protein_g),
        'carbs_g': round(carbs_g),
        'fat_g': round(fat_g),
        'fiber_g': round(fiber_g),
    }
