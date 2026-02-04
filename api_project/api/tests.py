from django.test import TestCase
from rest_framework.test import APIClient
from .models import Book


class BookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book1 = Book.objects.create(title='Book A', author='Author 1')
        self.book2 = Book.objects.create(title='Book B', author='Author 2')

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

    def test_create_book(self):
        data = {'title': 'Book C', 'author': 'Author 3'}
        response = self.client.post('/api/books_all/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Book.objects.count(), 3)
        obj = Book.objects.get(title='Book C')
        self.assertEqual(obj.author, 'Author 3')

    def test_retrieve_book(self):
        response = self.client.get(f'/api/books_all/{self.book1.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.book1.id)
        self.assertEqual(data['title'], self.book1.title)

    def test_update_book(self):
        payload = {'title': 'Book A Updated', 'author': 'Author 1'}
        response = self.client.put(f'/api/books_all/{self.book1.id}/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Book A Updated')

    def test_delete_book(self):
        response = self.client.delete(f'/api/books_all/{self.book2.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Book.objects.count(), 1)
