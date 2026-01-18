from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Book, Library


# Function-based View: List all books
def list_books(request):
    """
    Function-based view that displays all books in the database.
    This view retrieves all books and renders them in a template.
    """
    books = Book.objects.all()
    context = {
        'books': books
    }
    return render(request, 'relationship_app/list_books.html', context)


# Class-based View: Display specific library details
class LibraryDetailView(DetailView):
    """
    Class-based view that displays details of a specific library.
    Shows all books available in the library.
    Inherits from Django's DetailView for automatic handling of single object retrieval.
    """
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data for the template.
        """
        context = super().get_context_data(**kwargs)
        # The library object is already available as 'library' due to context_object_name
        # You can add more context data here if needed
        context['books_count'] = self.object.books.count()
        return context
