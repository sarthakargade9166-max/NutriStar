"""Comprehensive Unit, Integration & Security Tests for NutriStar Flask App"""

import unittest
import json
from app import create_app
from data.foods import FOODS, get_food_by_id, search_foods, get_foods_by_category


class NutriStarSecurityAndFunctionalityTests(unittest.TestCase):
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
        self.assertEqual(len(data), 581, f"Expected 581 foods from nutristar master database, got {len(data)}")

    def test_food_database_details_and_dual_casing(self):
        self.assertEqual(len(FOODS), 581)
        
        # Test sample food with rich details
        pav = get_food_by_id('pav-normal')
        self.assertIsNotNone(pav)
        self.assertEqual(pav['name'], 'Normal Pav')
        self.assertEqual(pav['name_hindi'], 'सामान्य पाव')
        self.assertEqual(pav['nameHindi'], 'सामान्य पाव')
        self.assertEqual(pav['calories_per_100g'], 268.0)
        self.assertEqual(pav['caloriesPer100g'], 268.0)
        self.assertEqual(pav['protein_per_100g'], 8.2)
        self.assertEqual(pav['grams_per_piece'], 35.0)
        self.assertEqual(pav['gramsPerPiece'], 35.0)
        self.assertEqual(pav['sugar_per_100g'], 3.0)
        self.assertEqual(pav['sodium_mg_per_100g'], 480.0)

        # Test brand / specialized items
        chitale = get_food_by_id('chitale-cow-milk')
        self.assertIsNotNone(chitale)
        self.assertIn('Chitale', chitale['name'])
        self.assertEqual(chitale['name_hindi'], 'चितळे गाईचे दूध')

    def test_api_foods_search_and_bounds(self):
        # Normal search
        res = self.client.get('/api/foods/search?q=roti')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any('roti' in f['name'].lower() or any('roti' in a.lower() for a in f.get('aliases', [])) for f in data))

        # Brand search
        res_chitale = self.client.get('/api/foods/search?q=chitale')
        self.assertEqual(res_chitale.status_code, 200)
        chitale_data = res_chitale.get_json()
        self.assertGreaterEqual(len(chitale_data), 3)

        # Category search
        res_cat = self.client.get('/api/foods/search?category=dairy')
        self.assertEqual(res_cat.status_code, 200)
        dairy_data = res_cat.get_json()
        self.assertTrue(all(f['category'] == 'dairy' for f in dairy_data))

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
        # Valid calculation for piece
        payload = {
            'food_id': 'chapati',
            'quantity': 2,
            'unit': 'piece'
        }
        res = self.client.post('/api/nutrition/calculate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('calories', data)
        self.assertIn('fiber', data)
        self.assertGreater(data['calories'], 100)

        # Valid calculation for pav (35g per piece)
        pav_payload = {
            'food_id': 'pav-normal',
            'quantity': 2,
            'unit': 'piece'
        }
        res_pav = self.client.post('/api/nutrition/calculate', json=pav_payload)
        self.assertEqual(res_pav.status_code, 200)
        pav_data = res_pav.get_json()
        self.assertEqual(pav_data['grams'], 70.0)
        self.assertIn('sugar', pav_data)
        self.assertIn('sodium', pav_data)

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
