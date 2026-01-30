from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Book
from .forms import BookForm
from .forms import ExampleForm

"""
Views with Permission-Based Access Control

This module implements views for book management with permission enforcement.
Each view uses the @permission_required decorator to check if the user has
the appropriate permission before allowing access.

SECURITY BEST PRACTICES IMPLEMENTED:
1. ORM Query Protection: All database queries use Django ORM which auto-escapes parameters
2. Input Validation: All user inputs validated through Django forms
3. Permission Checks: All views enforce permission requirements
4. Safe String Handling: No string concatenation in queries

Permission codes used:
- can_view_book: Permission to view/list books
- can_create_book: Permission to create new books
- can_edit_book: Permission to edit existing books
- can_delete_book: Permission to delete books

Users must be assigned to groups (Viewers, Editors, Admins) that have these
permissions assigned to access respective views.
"""


@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_list(request):
    """
    View to list all books with optional search functionality.
    
    Security Measures:
    - Uses Django ORM: .filter() and .exclude() prevent SQL injection
    - User input validated through Q objects with field lookups
    - Permission check ensures user can view books
    - Search query parameterized (not concatenated into SQL)
    
    Requires: can_view_book permission
    """
    books = Book.objects.all()
    search_query = request.GET.get('search', '').strip()
    
    # SECURE SEARCH IMPLEMENTATION
    # Using Django ORM's Q objects with parameterized queries
    # The search_query is passed as a parameter, not concatenated into SQL
    if search_query:
        # Safe query using ORM - user input is automatically escaped
        books = books.filter(
            Q(title__icontains=search_query) |  # icontains = case-insensitive contains
            Q(author__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    return render(request, 'bookshelf/book_list.html', context)


@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_detail(request, pk):
    """
    View to display details of a specific book.
    
    Security Measures:
    - Uses get_object_or_404() which properly escapes pk parameter
    - Permission check ensures user can view books
    
    Requires: can_view_book permission
    """
    # get_object_or_404 safely retrieves object - pk is properly escaped
    book = get_object_or_404(Book, pk=pk)
    context = {'book': book}
    return render(request, 'bookshelf/book_detail.html', context)


@permission_required('bookshelf.can_create_book', raise_exception=True)
@require_http_methods(["GET", "POST"])
def book_create(request):
    """
    View to create a new book.
    
    Security Measures:
    - Django form validates all input data before saving
    - form.is_valid() ensures data integrity
    - Permission check ensures user can create books
    - No direct SQL queries used
    
    Requires: can_create_book permission
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        # form.is_valid() validates input and protects against injection
        if form.is_valid():
            form.save()
            messages.success(request, 'Book created successfully!')
            return redirect('book-list')
    else:
        form = BookForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'bookshelf/book_form.html', context)


@permission_required('bookshelf.can_edit_book', raise_exception=True)
@require_http_methods(["GET", "POST"])
def book_edit(request, pk):
    """
    View to edit an existing book.
    
    Security Measures:
    - get_object_or_404 safely retrieves the book object
    - Django form validates all input data
    - form.is_valid() ensures data integrity before saving
    - Permission check ensures user can edit books
    
    Requires: can_edit_book permission
    """
    # Safely retrieve book object - pk is properly escaped
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        # Form validation protects against invalid/malicious input
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    context = {'form': form, 'book': book, 'action': 'Edit'}
    return render(request, 'bookshelf/book_form.html', context)


@permission_required('bookshelf.can_delete_book', raise_exception=True)
@require_http_methods(["GET", "POST"])
def book_delete(request, pk):
    """
    View to delete a book.
    
    Security Measures:
    - get_object_or_404 safely retrieves the book object
    - Permission check ensures only authorized users can delete
    - Confirmation required before deletion
    - No raw SQL queries used
    
    Requires: can_delete_book permission
    """
    # Safely retrieve book object - pk is properly escaped
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book-list')
    
    context = {'book': book}
    return render(request, 'bookshelf/book_confirm_delete.html', context)


@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_detail(request, pk):
    """
    View to display details of a specific book.
    Requires: can_view_book permission
    """
    book = get_object_or_404(Book, pk=pk)
    context = {'book': book}
    return render(request, 'bookshelf/book_detail.html', context)


@permission_required('bookshelf.can_create_book', raise_exception=True)
@require_http_methods(["GET", "POST"])
def book_create(request):
    """
    View to create a new book.
    Requires: can_create_book permission
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book created successfully!')
            return redirect('book-list')
    else:
        form = BookForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'bookshelf/book_form.html', context)


@permission_required('bookshelf.can_edit_book', raise_exception=True)
@require_http_methods(["GET", "POST"])
def book_edit(request, pk):
    """
    View to edit an existing book.
    Requires: can_edit_book permission
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    context = {'form': form, 'book': book, 'action': 'Edit'}
    return render(request, 'bookshelf/book_form.html', context)


@permission_required('bookshelf.can_delete_book', raise_exception=True)
@require_http_methods(["GET", "POST"])
def book_delete(request, pk):
    """
    View to delete a book.
    Requires: can_delete_book permission
    """
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book-list')
    
    context = {'book': book}
    return render(request, 'bookshelf/book_confirm_delete.html', context)


@require_http_methods(["GET", "POST"])
def example_view(request):
    """Simple example view demonstrating ExampleForm usage."""
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Form submitted successfully!')
            return redirect('example')
    else:
        form = ExampleForm()
    context = {'form': form}
    return render(request, 'bookshelf/form_example.html', context)

