from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Book
from .forms import BookForm


@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_list(request):
    """
    View to list all books.
    Requires: can_view_book permission
    """
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'bookshelf/book_list.html', context)


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

