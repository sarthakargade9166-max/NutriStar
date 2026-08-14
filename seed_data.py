"""Database initialization and seeding utilities for NutriStar."""

from database import db
from models import Food, User, Profile
from data.foods import FOODS


def seed_foods_if_empty():
    """Seeds master 581 Indian foods into SQLite if table is empty."""
    try:
        count = Food.query.count()
        if count == 0:
            print(f"Auto-seeding {len(FOODS)} foods into database...")
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
            print(f"Successfully seeded {len(FOODS)} foods into database.")
    except Exception as e:
        print(f"Seed error: {e}")
        db.session.rollback()


def seed_database():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_foods_if_empty()


if __name__ == '__main__':
    seed_database()
