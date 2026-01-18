"""
URL Configuration for relationship_app

This module defines URL patterns for the relationship_app views,
including both function-based and class-based views.
"""

from django.urls import path
from . import views
from .views import list_books
from .views import LibraryDetailView
from .views import UserLoginView, UserLogoutView

app_name = 'relationship_app'

urlpatterns = [
    # Function-based view: List all books
    path('books/', list_books, name='list_books'),
    
    # Class-based view: Display library details
    # The <int:pk> captures the library ID from the URL
    path('library/<int:pk>/', LibraryDetailView.as_view(), name='library_detail'),
    
    # Authentication views
    path('register/', views.register, name='register'),
    path('login/', UserLoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', UserLogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    
    # Role-based access control views
    path('admin/', views.admin_view, name='admin_view'),
    path('librarian/', views.librarian_view, name='librarian_view'),
    path('member/', views.member_view, name='member_view'),
]
