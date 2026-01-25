from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book-list'),
    path('books/<int:pk>/', views.book_detail, name='book-detail'),
    path('books/create/', views.book_create, name='book-create'),
    path('books/<int:pk>/edit/', views.book_edit, name='book-edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book-delete'),
]
