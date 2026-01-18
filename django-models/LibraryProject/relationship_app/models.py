from django.db import models
from django.contrib.auth.models import User

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
        permissions = [
            ('can_add_book', 'Can add a new book'),
            ('can_change_book', 'Can edit/change book details'),
            ('can_delete_book', 'Can delete a book'),
        ]


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


# UserProfile Model - Extends Django User with role-based access control
class UserProfile(models.Model):
    """
    UserProfile model to extend Django's built-in User model.
    Provides role-based access control with predefined roles.
    """
    
    # Role choices for different user types
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    
    # OneToOne relationship with Django's User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    
    # Role field with predefined choices
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        app_label = 'relationship_app'
