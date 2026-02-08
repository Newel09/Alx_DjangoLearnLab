from datetime import date
from rest_framework import serializers
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    Serializes Book model fields for API responses and requests.

    Includes custom validation to prevent publication_year being set in the future.
    """

    class Meta:
        model = Book
        fields = "__all__"

    def validate_publication_year(self, value: int) -> int:
        """
        Field-level validation: publication_year must not be in the future.
        """
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"publication_year cannot be greater than {current_year}."
            )
        return value


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializes Author plus related books using a nested serializer.

    `books` comes from Book.author.related_name="books" in the Book model.
    read_only=True means you can view an author's books in responses,
    but you won't create/update books through this Author serializer.
    """
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "books"]

