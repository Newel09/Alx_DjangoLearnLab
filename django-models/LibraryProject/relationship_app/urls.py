"""
URL Configuration for relationship_app

This module defines URL patterns for the relationship_app views,
including both function-based and class-based views.
"""

from django.urls import path
from .views import list_books
from .views import LibraryDetailView

app_name = 'relationship_app'

urlpatterns = [
    # Function-based view: List all books
    path('books/', list_books, name='list_books'),
    
    # Class-based view: Display library details
    # The <int:pk> captures the library ID from the URL
    path('library/<int:pk>/', LibraryDetailView.as_view(), name='library_detail'),
]
