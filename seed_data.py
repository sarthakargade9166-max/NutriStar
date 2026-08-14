"""Database initialization and seeding script for NutriStar."""

from app import create_app
from database import db
from models import Food, User, Profile
from data.foods import FOODS


def seed_database():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully.")

        # Seed Foods
        existing_count = Food.query.count()
        if existing_count == 0:
            print(f"Seeding {len(FOODS)} foods from master dataset...")
            for f in FOODS:
                aliases_str = ','.join(f.get('aliases', [])) if isinstance(f.get('aliases'), list) else str(f.get('aliases', ''))
                hindi_name = f.get('name_hindi') or f.get('hindi_name') or ''
                food = Food(
                    id=f['id'],
                    name=f['name'],
                    hindi_name=hindi_name,
                    category=f.get('category', 'general'),
                    serving_size=float(f.get('serving_size') or f.get('servingSize') or 1.0),
                    serving_unit=f.get('serving_unit') or f.get('servingUnit') or 'serving',
                    grams_per_serving=float(f.get('grams_per_serving') or f.get('gramsPerServing') or 100.0),
                    calories_100g=float(f.get('calories_100g') or f.get('caloriesPer100g') or 0.0),
                    protein_100g=float(f.get('protein_100g') or f.get('proteinPer100g') or 0.0),
                    carbs_100g=float(f.get('carbs_100g') or f.get('carbsPer100g') or 0.0),
                    fat_100g=float(f.get('fat_100g') or f.get('fatPer100g') or 0.0),
                    fiber_100g=float(f.get('fiber_100g') or f.get('fiberPer100g') or 0.0),
                    sugar_100g=float(f.get('sugar_100g') or f.get('sugarPer100g') or 0.0),
                    sodium_100g=float(f.get('sodium_100g') or f.get('sodiumPer100g') or 0.0),
                    saturated_fat_100g=float(f.get('saturated_fat_100g') or f.get('saturatedFatPer100g') or 0.0),
                    aliases=aliases_str
                )
                db.session.add(food)
            db.session.commit()
            print(f"Successfully seeded {len(FOODS)} food items into SQLite database.")
        else:
            print(f"Database already contains {existing_count} foods. Skipping food seed.")

        # Create demo user if none exists
        demo_user = User.query.filter_by(email='demo@nutristar.app').first()
        if not demo_user:
            demo_user = User(email='demo@nutristar.app')
            demo_user.set_password('demo1234')
            db.session.add(demo_user)
            db.session.commit()

            demo_profile = Profile(
                user_id=demo_user.id,
                name='Sarthak',
                age=25,
                gender='male',
                height_cm=175.0,
                current_weight_kg=75.0,
                target_weight_kg=70.0,
                activity_level='moderate',
                goal_type='lose',
                goal_control_mode='rate',
                target_rate_kg_per_week=0.5,
                calorie_target=1986,
                protein_target=135,
                carbs_target=220,
                fat_target=55,
                fiber_target=28
            )
            db.session.add(demo_profile)
            db.session.commit()
            print("Demo user created (demo@nutristar.app / demo1234).")


if __name__ == '__main__':
    seed_database()
