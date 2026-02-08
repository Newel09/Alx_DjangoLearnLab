# api/urls.py
from django.urls import path
from .views import (
    BookListCreateView,
    BookDetailView,
    BookUpdateView,
    BookDeleteView,
)

app_name = 'api'

urlpatterns = [
    # List and Create Books
    # GET /api/books/ -> List all books
    # POST /api/books/ -> Create a new book (authenticated users only)
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    
    # Retrieve a single book
    # GET /api/books/<pk>/ -> Retrieve book by ID
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    
    # Update a book
    # PUT /api/books/<pk>/update/ -> Full update (authenticated users only)
    # PATCH /api/books/<pk>/update/ -> Partial update (authenticated users only)
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book-update'),
    
    # Delete a book
    # DELETE /api/books/<pk>/delete/ -> Delete book (authenticated users only)
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book-delete'),
]
