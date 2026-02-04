from django.test import TestCase
from rest_framework.test import APIClient
from .models import Book


class BookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Book.objects.create(title='Book A', author='Author 1')
        Book.objects.create(title='Book B', author='Author 2')

    def test_list_books(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertIn('id', item)
            self.assertIn('title', item)
            self.assertIn('author', item)
