from rest_framework import serializers
from datetime import date
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model.

    Includes custom validation to ensure `publication_year` is not in the future.
    """

    class Meta:
        model = Book
        fields = '__all__'

    def validate_publication_year(self, value):
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError('Publication year cannot be in the future.')
        return value


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model.

    This serializer includes a nested list of books for the author using `BookSerializer`.
    The `books` field is read-only and dynamically populated from the related name on Book.
    """

    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
