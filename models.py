from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


def get_utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    meal_items = db.relationship('MealItem', backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), default='User')
    age = db.Column(db.Integer, default=25)
    gender = db.Column(db.String(10), default='male')
    height_cm = db.Column(db.Float, default=175.0)
    current_weight_kg = db.Column(db.Float, default=70.0)
    target_weight_kg = db.Column(db.Float, default=70.0)
    activity_level = db.Column(db.String(30), default='moderate')
    goal_type = db.Column(db.String(20), default='maintain')
    goal_control_mode = db.Column(db.String(20), default='rate')
    target_rate_kg_per_week = db.Column(db.Float, default=0.5)
    target_weeks = db.Column(db.Integer, default=12)
    calorie_target = db.Column(db.Integer, default=2000)
    protein_target = db.Column(db.Integer, default=120)
    carbs_target = db.Column(db.Integer, default=250)
    fat_target = db.Column(db.Integer, default=55)
    fiber_target = db.Column(db.Integer, default=28)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'height_cm': self.height_cm,
            'current_weight_kg': self.current_weight_kg,
            'target_weight_kg': self.target_weight_kg,
            'activity_level': self.activity_level,
            'goal_type': self.goal_type,
            'goal_control_mode': self.goal_control_mode,
            'target_rate_kg_per_week': self.target_rate_kg_per_week,
            'target_weeks': self.target_weeks,
            'calorie_target': self.calorie_target,
            'protein_target': self.protein_target,
            'carbs_target': self.carbs_target,
            'fat_target': self.fat_target,
            'fiber_target': self.fiber_target,
        }


class Food(db.Model):
    __tablename__ = 'foods'

    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    hindi_name = db.Column(db.String(150), index=True)
    category = db.Column(db.String(50), index=True)
    serving_size = db.Column(db.Float, default=1.0)
    serving_unit = db.Column(db.String(30), default='serving')
    grams_per_serving = db.Column(db.Float, default=100.0)
    calories_100g = db.Column(db.Float, default=0.0)
    protein_100g = db.Column(db.Float, default=0.0)
    carbs_100g = db.Column(db.Float, default=0.0)
    fat_100g = db.Column(db.Float, default=0.0)
    fiber_100g = db.Column(db.Float, default=0.0)
    sugar_100g = db.Column(db.Float, default=0.0)
    sodium_100g = db.Column(db.Float, default=0.0)
    saturated_fat_100g = db.Column(db.Float, default=0.0)
    aliases = db.Column(db.Text, default='')

    def to_dict(self):
        alias_list = [a.strip() for a in self.aliases.split(',') if a.strip()] if self.aliases else []
        return {
            'id': self.id,
            'name': self.name,
            'hindi_name': self.hindi_name,
            'category': self.category,
            'serving_size': self.serving_size,
            'serving_unit': self.serving_unit,
            'grams_per_serving': self.grams_per_serving,
            'calories_100g': self.calories_100g,
            'protein_100g': self.protein_100g,
            'carbs_100g': self.carbs_100g,
            'fat_100g': self.fat_100g,
            'fiber_100g': self.fiber_100g,
            'sugar_100g': self.sugar_100g,
            'sodium_100g': self.sodium_100g,
            'saturated_fat_100g': self.saturated_fat_100g,
            'aliases': alias_list
        }


class MealItem(db.Model):
    __tablename__ = 'meal_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False, index=True)
    meal_type = db.Column(db.String(20), nullable=False, index=True)
    food_id = db.Column(db.String(100), nullable=False)
    food_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(30), nullable=False, default='serving')
    grams = db.Column(db.Float, nullable=False, default=100.0)
    calories = db.Column(db.Float, nullable=False, default=0.0)
    protein = db.Column(db.Float, nullable=False, default=0.0)
    carbs = db.Column(db.Float, nullable=False, default=0.0)
    fat = db.Column(db.Float, nullable=False, default=0.0)
    fiber = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date,
            'meal_type': self.meal_type,
            'food_id': self.food_id,
            'food_name': self.food_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'grams': round(self.grams, 1),
            'calories': round(self.calories, 1),
            'protein': round(self.protein, 1),
            'carbs': round(self.carbs, 1),
            'fat': round(self.fat, 1),
            'fiber': round(self.fiber, 1),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
