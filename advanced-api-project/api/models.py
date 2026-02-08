from django.db import models


class Author(models.Model):
    """
    Stores an author's basic information.

    Relationship:
    - An Author can have many Book records (one-to-many).
    - Access related books via `author.books.all()` because Book.author uses related_name="books".
    """
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    """
    Stores a book record.

    Fields:
    - title: book title
    - publication_year: year of publication
    - author: ForeignKey to Author (each book belongs to one author)

    Relationship details:
    - ForeignKey creates a one-to-many relationship: one Author -> many Books.
    - on_delete=models.CASCADE means deleting an Author deletes their Books too.
    """
    title = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.publication_year})"
