from django.test import TestCase
from .models import Author, Book
from .serializers import BookSerializer, AuthorSerializer
from rest_framework.exceptions import ValidationError
from datetime import date


class SerializerTests(TestCase):
    def test_book_publication_year_validation(self):
        next_year = date.today().year + 1
        author = Author.objects.create(name='Validation Author')
        serializer = BookSerializer(data={'title': 'Future Book', 'publication_year': next_year, 'author': author.id})
        with self.assertRaises(ValidationError):
            # Trigger validation
            serializer.is_valid(raise_exception=True)

    def test_author_serializer_includes_nested_books(self):
        author = Author.objects.create(name='Test Author')
        book1 = Book.objects.create(title='One', publication_year=2000, author=author)
        book2 = Book.objects.create(title='Two', publication_year=2005, author=author)

        serializer = AuthorSerializer(author)
        data = serializer.data
        self.assertEqual(data['name'], 'Test Author')
        self.assertIn('books', data)
        self.assertEqual(len(data['books']), 2)
        titles = {b['title'] for b in data['books']}
        self.assertEqual(titles, {'One', 'Two'})
