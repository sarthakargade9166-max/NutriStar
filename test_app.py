import unittest
from datetime import datetime, timedelta
import pytz
from app import create_app
from database import db
from models import User, Profile, Food, MealItem
from nutrition import (
    calculate_food_nutrition,
    calculate_tdee,
    calculate_targets,
    get_personalized_quick_add,
    get_unit_options,
    get_ist_today,
    get_ist_default_meal,
    get_rolling_10_days
)


class TestNutriStarApp(unittest.TestCase):
    """
    Comprehensive test suite for NutriStar application.
    Tests core calculation engines, database models, security headers,
    server-side input validation, authorization/IDOR defense, CSRF, and REST API.
    """

    @classmethod
    def setUpClass(cls):
        class TestConfig:
            TESTING = True
            SECRET_KEY = 'test-secret-key-nutristar'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            TEMPLATES_AUTO_RELOAD = True
            SESSION_COOKIE_HTTPONLY = True
            SESSION_COOKIE_SAMESITE = 'Lax'
            SESSION_COOKIE_SECURE = False

        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # -------------------------------------------------------------
    # 1. Calculation Engine Tests (nutrition.py)
    # -------------------------------------------------------------
    def test_calculate_tdee_male_and_female(self):
        tdee_male = calculate_tdee(70, 175, 25, 'male', 'moderate')
        self.assertEqual(tdee_male, 2594)

        tdee_female = calculate_tdee(60, 160, 25, 'female', 'sedentary')
        self.assertEqual(tdee_female, 1577)

    def test_calculate_targets_loss_and_gain(self):
        targets_loss = calculate_targets(
            current_weight=80.0,
            target_weight=75.0,
            height_cm=175.0,
            age=30,
            gender='male',
            activity_level='moderate',
            goal_control_mode='rate',
            target_rate_kg_per_week=0.5
        )
        self.assertEqual(targets_loss['goal_type'], 'lose')
        self.assertTrue(targets_loss['calories'] < targets_loss['tdee'])
        self.assertGreater(targets_loss['protein'], 0)
        self.assertGreater(targets_loss['carbs'], 0)
        self.assertGreater(targets_loss['fat'], 0)
        self.assertGreater(targets_loss['fiber'], 0)

        targets_maintain = calculate_targets(
            current_weight=70.0,
            target_weight=70.0,
            height_cm=175.0,
            age=25,
            gender='male',
            activity_level='moderate'
        )
        self.assertEqual(targets_maintain['goal_type'], 'maintain')
        self.assertEqual(targets_maintain['calories'], targets_maintain['tdee'])

    def test_calculate_food_nutrition_scaling(self):
        food = Food.query.filter_by(id='chapati').first()
        self.assertIsNotNone(food)

        scaled_1 = calculate_food_nutrition(food, 1.0, 'piece')
        self.assertEqual(scaled_1['grams'], 35.0)
        expected_cals_1 = round((food.calories_100g * 35.0) / 100.0, 1)
        self.assertAlmostEqual(scaled_1['calories'], expected_cals_1, delta=0.2)

        scaled_2 = calculate_food_nutrition(food, 2.0, 'piece')
        self.assertEqual(scaled_2['grams'], 70.0)
        expected_cals_2 = round((food.calories_100g * 70.0) / 100.0, 1)
        self.assertAlmostEqual(scaled_2['calories'], expected_cals_2, delta=0.2)

        scaled_100g = calculate_food_nutrition(food, 100.0, 'g')
        self.assertEqual(scaled_100g['grams'], 100.0)
        self.assertAlmostEqual(scaled_100g['calories'], round(food.calories_100g, 1), delta=0.2)

    def test_get_unit_options_heuristics(self):
        beverage = Food.query.filter_by(id='filter-coffee').first() or {'name': 'Filter Coffee', 'category': 'beverages', 'serving_unit': 'cup'}
        unit_opts_bev = get_unit_options(beverage)
        unit_values_bev = [u['value'] for u in unit_opts_bev]
        self.assertIn('ml', unit_values_bev)
        self.assertIn('cup', unit_values_bev)

        chapati = Food.query.filter_by(id='chapati').first()
        unit_opts_chapati = get_unit_options(chapati)
        unit_values_chapati = [u['value'] for u in unit_opts_chapati]
        self.assertIn('piece', unit_values_chapati)
        self.assertIn('g', unit_values_chapati)

    def test_temporal_helpers(self):
        today_ist = get_ist_today()
        self.assertRegex(today_ist, r'^\d{4}-\d{2}-\d{2}$')

        default_meal = get_ist_default_meal()
        self.assertIn(default_meal, ['breakfast', 'lunch', 'snack', 'dinner'])

        rolling_10 = get_rolling_10_days()
        self.assertEqual(len(rolling_10), 10)
        self.assertTrue(rolling_10[0]['is_today'])

    # -------------------------------------------------------------
    # 2. Database & Seeding Tests
    # -------------------------------------------------------------
    def test_database_seeding_and_food_count(self):
        count = Food.query.count()
        self.assertGreaterEqual(count, 580, "Expected at least 580 seeded foods")

    def test_user_password_hashing(self):
        user = User(email='testuser@nutristar.app')
        user.set_password('SecretPassword123')
        self.assertNotEqual(user.password_hash, 'SecretPassword123')
        self.assertTrue(user.check_password('SecretPassword123'))
        self.assertFalse(user.check_password('WrongPassword'))

    # -------------------------------------------------------------
    # 3. Security Headers & CSP Tests
    # -------------------------------------------------------------
    def test_security_headers_and_csp(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIn('Permissions-Policy', response.headers)

        csp = response.headers.get('Content-Security-Policy')
        self.assertIsNotNone(csp)
        self.assertIn("default-src 'self'", csp)
        self.assertIn("fonts.googleapis.com", csp)
        self.assertIn("fonts.gstatic.com", csp)
        self.assertIn("frame-ancestors 'none'", csp)

    # -------------------------------------------------------------
    # 4. Page Routes Tests
    # -------------------------------------------------------------
    def test_page_routes_render_success(self):
        routes_to_test = [
            ('/', 302),
            ('/dashboard', 200),
            ('/log-food', 200),
            ('/history', 200),
            ('/profile', 200),
            ('/onboarding', 200),
            ('/settings', 200),
        ]
        for path, expected_status in routes_to_test:
            res = self.client.get(path)
            self.assertEqual(res.status_code, expected_status, f"Failed for {path}")

    def test_history_day_view(self):
        today = get_ist_today()
        res = self.client.get(f'/history/{today}')
        self.assertEqual(res.status_code, 200)

        # Malformed date redirects cleanly
        res_bad = self.client.get('/history/not-a-valid-date')
        self.assertEqual(res_bad.status_code, 302)

    # -------------------------------------------------------------
    # 5. RESTful API & Server-Side Input Validation Tests
    # -------------------------------------------------------------
    def test_api_food_search(self):
        res = self.client.get('/api/foods/search?q=rice')
        self.assertEqual(res.status_code, 200)
        foods = res.get_json()
        self.assertIsInstance(foods, list)
        self.assertGreater(len(foods), 0)

        res_empty = self.client.get('/api/foods/search?q=')
        self.assertEqual(res_empty.status_code, 200)
        self.assertLessEqual(len(res_empty.get_json()), 25)

    def test_api_get_food_details(self):
        res = self.client.get('/api/foods/chapati')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['id'], 'chapati')
        self.assertIn('unit_options', data)

        res_invalid = self.client.get('/api/foods/non-existent-food-id-xyz')
        self.assertEqual(res_invalid.status_code, 404)

    def test_api_calculate_endpoint(self):
        payload = {
            'food_id': 'chapati',
            'quantity': 2,
            'unit': 'piece'
        }
        res = self.client.post('/api/calculate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['grams'], 70.0)
        self.assertGreater(data['calories'], 0)

        # Invalid quantity
        res_bad = self.client.post('/api/calculate', json={'food_id': 'chapati', 'quantity': -5})
        self.assertEqual(res_bad.status_code, 400)

    def test_api_input_boundaries_on_logging(self):
        # 1. Negative quantity rejected
        res_neg = self.client.post('/api/log', json={
            'food_id': 'chapati',
            'meal_type': 'lunch',
            'quantity': -2.0,
            'unit': 'piece'
        })
        self.assertEqual(res_neg.status_code, 400)

        # 2. Invalid meal category rejected
        res_cat = self.client.post('/api/log', json={
            'food_id': 'chapati',
            'meal_type': 'unsupported_category',
            'quantity': 1.0,
            'unit': 'piece'
        })
        self.assertEqual(res_cat.status_code, 400)

        # 3. Invalid date (future date) rejected
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        res_future = self.client.post('/api/log', json={
            'food_id': 'chapati',
            'meal_type': 'lunch',
            'quantity': 1.0,
            'unit': 'piece',
            'date': future_date
        })
        self.assertEqual(res_future.status_code, 400)

        # 4. Invalid date (outside 10-day window) rejected
        ancient_date = '2020-01-01'
        res_ancient = self.client.post('/api/log', json={
            'food_id': 'chapati',
            'meal_type': 'lunch',
            'quantity': 1.0,
            'unit': 'piece',
            'date': ancient_date
        })
        self.assertEqual(res_ancient.status_code, 400)

    def test_api_meal_logging_lifecycle_and_user_isolation(self):
        with self.app.test_client() as client_a:
            # User A logs a meal item
            res_log = client_a.post('/api/log', json={
                'food_id': 'chapati',
                'meal_type': 'lunch',
                'quantity': 2,
                'unit': 'piece',
                'date': get_ist_today()
            })
            self.assertEqual(res_log.status_code, 201)
            item_a_id = res_log.get_json()['item']['id']

            # User A updates the meal item
            res_update = client_a.put(f'/api/meal-items/{item_a_id}', json={
                'quantity': 3.0,
                'unit': 'piece',
                'meal_type': 'lunch'
            })
            self.assertEqual(res_update.status_code, 200)
            self.assertEqual(res_update.get_json()['item']['quantity'], 3.0)

            # User B (separate session) attempts unauthorized access / IDOR attack on User A's item
            with self.app.test_client() as client_b:
                # User B tries to update User A's item
                res_unauth_update = client_b.put(f'/api/meal-items/{item_a_id}', json={
                    'quantity': 10.0,
                    'unit': 'piece',
                    'meal_type': 'lunch'
                })
                self.assertEqual(res_unauth_update.status_code, 404, "User B must not be able to edit User A's item")

                # User B tries to delete User A's item
                res_unauth_delete = client_b.delete(f'/api/meal-items/{item_a_id}')
                self.assertEqual(res_unauth_delete.status_code, 404, "User B must not be able to delete User A's item")

            # User A deletes their own item
            res_delete = client_a.delete(f'/api/meal-items/{item_a_id}')
            self.assertEqual(res_delete.status_code, 200)

    def test_csrf_protection_enforcement(self):
        class NonTestingConfig:
            TESTING = False
            SECRET_KEY = 'test-secret-key-nutristar'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SESSION_COOKIE_HTTPONLY = True
            SESSION_COOKIE_SAMESITE = 'Lax'

        csrf_app = create_app(NonTestingConfig)
        with csrf_app.test_client() as c:
            # 1. State-changing POST without CSRF token must return 403 Forbidden
            res_no_token = c.post('/api/calculate', json={'food_id': 'chapati', 'quantity': 1})
            self.assertEqual(res_no_token.status_code, 403)
            self.assertEqual(res_no_token.get_json()['error'], 'Forbidden')

            # 2. Get a page to initialize session and retrieve CSRF token
            c.get('/dashboard')
            with c.session_transaction() as sess:
                valid_token = sess.get('csrf_token')
            self.assertIsNotNone(valid_token)

            # 3. Post with valid X-CSRFToken header succeeds
            res_with_token = c.post(
                '/api/calculate',
                json={'food_id': 'chapati', 'quantity': 1},
                headers={'X-CSRFToken': valid_token}
            )
            self.assertEqual(res_with_token.status_code, 200)

    def test_api_active_date_management(self):
        res_get = self.client.get('/api/active-date')
        self.assertEqual(res_get.status_code, 200)
        self.assertIn('active_date', res_get.get_json())

        today = get_ist_today()
        res_post = self.client.post('/api/active-date', json={'date': today})
        self.assertEqual(res_post.status_code, 200)
        self.assertEqual(res_post.get_json()['active_date'], today)

    def test_api_quick_add(self):
        res = self.client.get('/api/quick-add')
        self.assertEqual(res.status_code, 200)
        quick_foods = res.get_json()
        self.assertIsInstance(quick_foods, list)
        self.assertGreater(len(quick_foods), 0)

    def test_api_export_data(self):
        res = self.client.get('/api/export-data')
        self.assertEqual(res.status_code, 200)
        export_payload = res.get_json()
        self.assertIn('profile', export_payload)
        self.assertIn('meal_logs', export_payload)


if __name__ == '__main__':
    unittest.main()
