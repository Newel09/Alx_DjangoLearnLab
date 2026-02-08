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

    def test_create_book_requires_auth(self):
        # Unauthenticated requests should be denied for create
        data = {'title': 'Book C', 'author': 'Author 3'}
        response = self.client.post('/api/books_all/', data, format='json')
        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(Book.objects.count(), 2)

    def test_crud_with_token(self):
        # Create a user and obtain a token
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token

        user = User.objects.create_user(username='tester', password='pass')
        resp = self.client.post('/api/token-auth/', {'username': 'tester', 'password': 'pass'}, format='json')
        self.assertEqual(resp.status_code, 200)
        token = resp.json().get('token')
        self.assertIsNotNone(token)

        # Authenticate with token and create
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        data = {'title': 'Book C', 'author': 'Author 3'}
        resp = self.client.post('/api/books_all/', data, format='json')
        self.assertEqual(resp.status_code, 201)
        created_id = resp.json().get('id')
        self.assertIsNotNone(created_id)

        # Retrieve
        resp = self.client.get(f'/api/books_all/{created_id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('title'), 'Book C')

        # Update
        payload = {'title': 'Book C Updated', 'author': 'Author 3'}
        resp = self.client.put(f'/api/books_all/{created_id}/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('title'), 'Book C Updated')

        # Delete
        resp = self.client.delete(f'/api/books_all/{created_id}/')
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Book.objects.filter(id=created_id).count(), 0)
