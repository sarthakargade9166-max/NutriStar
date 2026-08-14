"""Comprehensive Unit, Integration & Security Tests for NutriTrack Flask App"""

import unittest
import json
from app import create_app


class NutriTrackSecurityAndFunctionalityTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_pages_routes(self):
        routes = ['/', '/dashboard', '/onboarding', '/log-food', '/meals', '/analytics', '/ai-insights', '/profile', '/settings']
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route failed: {r}")

    def test_security_headers(self):
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(res.headers.get('X-Frame-Options'), 'DENY')
        self.assertIn("default-src 'self'", res.headers.get('Content-Security-Policy', ''))
        self.assertEqual(res.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

    def test_api_foods(self):
        res = self.client.get('/api/foods')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 50)

    def test_api_foods_search_and_bounds(self):
        # Normal search
        res = self.client.get('/api/foods/search?q=roti')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any('roti' in f['name'].lower() or any('roti' in a.lower() for a in f.get('aliases', [])) for f in data))

        # Extreme length query sanitization
        long_query = 'a' * 500
        res_long = self.client.get(f'/api/foods/search?q={long_query}')
        self.assertEqual(res_long.status_code, 200)

    def test_api_targets_validation(self):
        # Normal targets
        profile = {
            'weight_kg': 75,
            'height_cm': 178,
            'age': 27,
            'sex': 'male',
            'activity_level': 'moderate',
            'goal': 'muscle'
        }
        res = self.client.post('/api/targets', json=profile)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('calories_kcal', data)
        self.assertGreater(data['calories_kcal'], 1800)

        # Extreme values / boundary protection
        extreme_profile = {
            'weight_kg': -999,  # Clamped to 20kg minimum
            'height_cm': 9999,  # Clamped to 300cm maximum
            'age': -50,         # Clamped to 5 years minimum
            'sex': 'invalid_sex'
        }
        res_extreme = self.client.post('/api/targets', json=extreme_profile)
        self.assertEqual(res_extreme.status_code, 200)
        data_extreme = res_extreme.get_json()
        self.assertGreater(data_extreme['calories_kcal'], 500)

    def test_api_nutrition_calculate_and_negative_rejection(self):
        # Valid calculation
        payload = {
            'food_id': 'chapati',
            'quantity': 2,
            'unit': 'piece'
        }
        res = self.client.post('/api/nutrition/calculate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('calories', data)
        self.assertGreater(data['calories'], 100)

        # Negative quantity rejection (Business logic defense)
        negative_payload = {
            'food_id': 'chapati',
            'quantity': -5,
            'unit': 'piece'
        }
        res_neg = self.client.post('/api/nutrition/calculate', json=negative_payload)
        self.assertEqual(res_neg.status_code, 400)
        self.assertIn('error', res_neg.get_json())

    def test_api_error_handlers(self):
        # 404 on API returns clean JSON, not stack trace
        res = self.client.get('/api/nonexistent-endpoint')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.get_json().get('error'), 'Not Found')

        # 405 on API
        res_method = self.client.post('/api/foods')
        self.assertEqual(res_method.status_code, 405)
        self.assertEqual(res_method.get_json().get('error'), 'Method Not Allowed')


if __name__ == '__main__':
    unittest.main()
