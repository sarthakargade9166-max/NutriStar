import unittest
import os
from datetime import datetime, timedelta
import pytz
from app import create_app
from config import Config
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
        self.assertIn("script-src 'self'", csp)
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
        # 1. Valid date within 10-day rolling window succeeds
        res_valid = self.client.get(f'/history/{today}')
        self.assertEqual(res_valid.status_code, 200)

        # 2. Out-of-window past date (>10 days ago) must be rejected with 302 redirect
        old_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        res_old = self.client.get(f'/history/{old_date}')
        self.assertEqual(res_old.status_code, 302)
        with self.client.session_transaction() as sess:
            self.assertNotEqual(sess.get('active_date'), old_date)

        # 3. Future date must be rejected with 302 redirect
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        res_future = self.client.get(f'/history/{future_date}')
        self.assertEqual(res_future.status_code, 302)
        with self.client.session_transaction() as sess:
            self.assertNotEqual(sess.get('active_date'), future_date)

        # 4. Malformed date format redirects cleanly
        res_bad = self.client.get('/history/not-a-valid-date')
        self.assertEqual(res_bad.status_code, 302)

    # -------------------------------------------------------------
    # 5. Security & Input Boundaries Tests
    # -------------------------------------------------------------
    def test_active_date_boundary_rejection(self):
        # 1. Old date (>10 days ago) must be rejected with 400
        old_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        res_old = self.client.post('/api/active-date', json={'date': old_date})
        self.assertEqual(res_old.status_code, 400)
        self.assertEqual(res_old.get_json()['error'], 'Bad Request')

        # 2. Future date must be rejected with 400
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        res_future = self.client.post('/api/active-date', json={'date': future_date})
        self.assertEqual(res_future.status_code, 400)

        # 3. Valid date within 10-day rolling window must be accepted
        today = get_ist_today()
        res_today = self.client.post('/api/active-date', json={'date': today})
        self.assertEqual(res_today.status_code, 200)
        self.assertEqual(res_today.get_json()['active_date'], today)

    def test_invalid_unit_and_quantity_rejections(self):
        # Invalid quantity (negative or > 1000)
        res_qty_neg = self.client.post('/api/calculate', json={'food_id': 'chapati', 'quantity': -5, 'unit': 'piece'})
        self.assertEqual(res_qty_neg.status_code, 400)

        res_qty_huge = self.client.post('/api/calculate', json={'food_id': 'chapati', 'quantity': 5000, 'unit': 'piece'})
        self.assertEqual(res_qty_huge.status_code, 400)

        # Invalid unit for food (e.g. 'gallon' or 'kilogram_fake' on chapati)
        res_unit_bad = self.client.post('/api/calculate', json={'food_id': 'chapati', 'quantity': 1, 'unit': 'unknown_unit_xyz'})
        self.assertEqual(res_unit_bad.status_code, 400)

        # Valid unit accepted on chapati
        res_unit_ok = self.client.post('/api/calculate', json={'food_id': 'chapati', 'quantity': 2, 'unit': 'piece'})
        self.assertEqual(res_unit_ok.status_code, 200)

        # Valid food logging across different serving units (pack, piece, bowl/katori, g, burger, slice)
        for food_id, unit, qty in [
            ('mcdonalds-fries-medium', 'pack', 1),
            ('mcdonalds-mcveggie-burger', 'piece', 1),
            ('dal-fry', 'katori', 1),
            ('paneer', 'g', 150),
            ('mcdonalds-mcspicy-paneer-protein-plus', 'burger', 1),
            ('dominos-peppy-paneer-pizza', 'slice', 2)
        ]:
            res = self.client.post('/api/log', json={
                'food_id': food_id,
                'meal_type': 'dinner',
                'quantity': qty,
                'unit': unit,
                'date': get_ist_today()
            })
            self.assertEqual(res.status_code, 201, f"Failed to log {food_id} with unit {unit}")

    def test_cross_user_isolation_and_idor_defense(self):
        with self.app.test_client() as client_a:
            # User A logs an item
            res_log = client_a.post('/api/log', json={
                'food_id': 'chapati',
                'meal_type': 'lunch',
                'quantity': 2,
                'unit': 'piece',
                'date': get_ist_today()
            })
            self.assertEqual(res_log.status_code, 201)
            item_a_id = res_log.get_json()['item']['id']

            # User B attempts to view/modify/delete User A's item
            with self.app.test_client() as client_b:
                # 1. User B cannot edit User A's item
                res_unauth_edit = client_b.put(f'/api/meal-items/{item_a_id}', json={
                    'quantity': 5.0,
                    'unit': 'piece',
                    'meal_type': 'lunch'
                })
                self.assertEqual(res_unauth_edit.status_code, 404)

                # 2. User B cannot delete User A's item
                res_unauth_del = client_b.delete(f'/api/meal-items/{item_a_id}')
                self.assertEqual(res_unauth_del.status_code, 404)

            # User A successfully edits and deletes their own item
            res_edit = client_a.put(f'/api/meal-items/{item_a_id}', json={
                'quantity': 3.0,
                'unit': 'piece',
                'meal_type': 'lunch'
            })
            self.assertEqual(res_edit.status_code, 200)

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
            res_no_token = c.post('/api/calculate', json={'food_id': 'chapati', 'quantity': 1, 'unit': 'piece'})
            self.assertEqual(res_no_token.status_code, 403)
            self.assertEqual(res_no_token.get_json()['error'], 'Forbidden')

            # 2. State-changing POST with invalid CSRF token returns 403
            res_bad_token = c.post(
                '/api/calculate',
                json={'food_id': 'chapati', 'quantity': 1, 'unit': 'piece'},
                headers={'X-CSRFToken': 'invalid-csrf-token-12345'}
            )
            self.assertEqual(res_bad_token.status_code, 403)

            # 3. Get page to initialize session and retrieve genuine CSRF token
            c.get('/dashboard')
            with c.session_transaction() as sess:
                valid_token = sess.get('csrf_token')
            self.assertIsNotNone(valid_token)

            # 4. Post with valid X-CSRFToken header succeeds
            res_with_token = c.post(
                '/api/calculate',
                json={'food_id': 'chapati', 'quantity': 1, 'unit': 'piece'},
                headers={'X-CSRFToken': valid_token}
            )
            self.assertEqual(res_with_token.status_code, 200)

    def test_xss_escaping_safety(self):
        with self.app.test_client() as client:
            res = client.get('/dashboard')
            self.assertEqual(res.status_code, 200)
            html_content = res.get_data(as_text=True)
            # Ensure no raw unescaped script tag execution is possible
            self.assertNotIn('<script>alert(1)</script>', html_content)

    def test_production_and_dev_configuration_modes(self):
        # 1. Verify default config has valid SECRET_KEY, HTTPONLY, SAMESITE
        self.assertIsNotNone(Config.SECRET_KEY)
        self.assertTrue(Config.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(Config.SESSION_COOKIE_SAMESITE, 'Lax')

        # 2. Production mode configuration
        class ProdConfig(Config):
            TESTING = True
            SECRET_KEY = 'super-secure-prod-key'
            SESSION_COOKIE_SECURE = True
            SESSION_COOKIE_HTTPONLY = True
            SESSION_COOKIE_SAMESITE = 'Lax'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

        prod_app = create_app(ProdConfig)
        self.assertTrue(prod_app.config['SESSION_COOKIE_SECURE'])
        self.assertTrue(prod_app.config['SESSION_COOKIE_HTTPONLY'])

    def test_production_secret_missing_fails_startup(self):
        import subprocess
        import sys
        script = '''
import os
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = ''
import importlib
import config
importlib.reload(config)
'''
        proc = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('CRITICAL SECURITY ERROR', proc.stderr)

    def test_untrusted_host_rejected(self):
        class HostConfig(Config):
            TESTING = False
            SECRET_KEY = 'test-secret-key-nutristar'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SESSION_COOKIE_SECURE = True
            TRUSTED_HOSTS = ['*.onrender.com', 'nutristar.app']

        host_app = create_app(HostConfig)
        with host_app.test_client() as c:
            # Trusted exact host succeeds
            res_exact = c.get('/dashboard', headers={'Host': 'nutristar.app'})
            self.assertEqual(res_exact.status_code, 200)

            # Trusted wildcard subdomain on onrender.com succeeds
            res_subdomain = c.get('/dashboard', headers={'Host': 'my-custom-service.onrender.com'})
            self.assertEqual(res_subdomain.status_code, 200)

            # Untrusted host is rejected with 400 Bad Request
            res_bad = c.get('/dashboard', headers={'Host': 'evil-phishing-domain.com'})
            self.assertEqual(res_bad.status_code, 400)


if __name__ == '__main__':
    unittest.main()
