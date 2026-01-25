from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Custom User Manager
class CustomUserManager(BaseUserManager):
    """
    Custom user manager for the CustomUser model.
    Handles creation of regular users and superusers.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds additional fields for user information: date_of_birth and profile_photo.
    """
    
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True, help_text="User's date of birth")
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True, help_text="User's profile photo")
    
    # Use custom manager
    objects = CustomUserManager()
    
    # Set email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"
    
    class Meta:
        app_label = 'relationship_app'
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'

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


# UserProfile Model - Extends CustomUser with role-based access control
class UserProfile(models.Model):
    """
    UserProfile model to extend the custom user model.
    Provides role-based access control with predefined roles.
    """
    
    # Role choices for different user types
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    
    # OneToOne relationship with the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='userprofile')
    
    # Role field with predefined choices
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        app_label = 'relationship_app'
