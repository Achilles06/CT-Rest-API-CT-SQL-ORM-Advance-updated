# tests/test_pagination.py

import unittest
from app import create_app
from models import db

class TestPagination(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_orders_pagination(self):
        response = self.client.get('/orders?page=1&per_page=5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('orders', data)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('pages', data)
        self.assertIn('per_page', data)

if __name__ == '__main__':
    unittest.main()
