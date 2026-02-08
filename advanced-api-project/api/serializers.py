from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

    def validate(self, attrs):
        """
        Object-level validation.
        Runs for both create and update.
        """
        # Example rule: title cannot be empty/whitespace if your model has `title`
        title = attrs.get("title")
        if title is not None and not str(title).strip():
            raise serializers.ValidationError({"title": "Title cannot be blank."})

        return attrs

