from django.db import models

# Author Model - represents book authors
class Author(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'relationship_app'


# Book Model - uses ForeignKey to Author (One Author can have many Books)
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    
    def __str__(self):
        return self.title
    
    class Meta:
        app_label = 'relationship_app'


# Library Model - uses ManyToMany to Book (One Library can have many Books, and one Book can be in many Libraries)
class Library(models.Model):
    name = models.CharField(max_length=200)
    books = models.ManyToManyField(Book, related_name='libraries')
    
    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'relationship_app'


# Librarian Model - uses OneToOne to Library (One Librarian manages one Library, and one Library has one Librarian)
class Librarian(models.Model):
    name = models.CharField(max_length=100)
    library = models.OneToOneField(Library, on_delete=models.CASCADE, related_name='librarian')
    
    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'relationship_app'
