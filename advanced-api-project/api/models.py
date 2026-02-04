from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class Author(models.Model):
    """Author represents a book author.

    Fields:
    - name: The author's full name.

    The Author -> Book relationship is one-to-many: an Author can have multiple Book instances.
    Use the related_name `books` on Book to access this author's books (`author.books.all()`).
    """

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Book(models.Model):
    """Book represents a single published work.

    Fields:
    - title: The title of the book.
    - publication_year: Year the book was published (validated not to be in the future).
    - author: ForeignKey to `Author` establishing a many-to-one relationship.
    """

    title = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)

    def clean(self):
        """Validate that the publication_year is not in the future."""
        current_year = date.today().year
        if self.publication_year > current_year:
            raise ValidationError({'publication_year': 'Publication year cannot be in the future.'})

    def save(self, *args, **kwargs):
        # Call full_clean to ensure model-level validation runs on save
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.publication_year}) by {self.author}"
