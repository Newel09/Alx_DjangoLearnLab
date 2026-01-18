from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Book
from .models import Library


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


# Authentication Views

def register(request):
    """
    Function-based view for user registration.
    Allows new users to create an account using the built-in UserCreationForm.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the user after registration
            login(request, user)
            return redirect('relationship_app:list_books')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'relationship_app/register.html', context)


def user_login(request):
    """
    Function-based view for user login.
    Authenticates users and manages user sessions.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('relationship_app:list_books')
    else:
        form = AuthenticationForm()
    
    context = {'form': form}
    return render(request, 'relationship_app/login.html', context)


def user_logout(request):
    """
    Function-based view for user logout.
    Terminates the user session and redirects to logout confirmation page.
    """
    logout(request)
    return render(request, 'relationship_app/logout.html')


# Class-based Authentication Views

class UserLoginView(LoginView):
    """
    Class-based view for user login using Django's built-in LoginView.
    Inherits from Django's LoginView for automatic authentication handling.
    """
    template_name = 'relationship_app/login.html'
    form_class = AuthenticationForm
    success_url = 'relationship_app:list_books'
    
    def get_success_url(self):
        """
        Redirect to the list_books page after successful login.
        """
        from django.urls import reverse
        return reverse('relationship_app:list_books')


class UserLogoutView(LogoutView):
    """
    Class-based view for user logout using Django's built-in LogoutView.
    Inherits from Django's LogoutView for automatic session termination.
    """
    template_name = 'relationship_app/logout.html'


# Role-Based Access Control Views

def is_admin(user):
    """
    Check if the user has the 'admin' role.
    """
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'admin'


def is_librarian(user):
    """
    Check if the user has the 'librarian' role.
    """
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'librarian'


def is_member(user):
    """
    Check if the user has the 'member' role.
    """
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'member'


@user_passes_test(is_admin)
def admin_view(request):
    """
    View accessible only to users with 'Admin' role.
    Displays administrative content and controls.
    """
    context = {
        'role': 'Admin',
        'message': 'Welcome to the Admin Dashboard',
        'description': 'You have administrative access to manage the library system.',
    }
    return render(request, 'relationship_app/admin_view.html', context)


@user_passes_test(is_librarian)
def librarian_view(request):
    """
    View accessible only to users with 'Librarian' role.
    Displays librarian-specific content and controls.
    """
    context = {
        'role': 'Librarian',
        'message': 'Welcome to the Librarian Dashboard',
        'description': 'You have access to manage library resources and patron information.',
    }
    return render(request, 'relationship_app/librarian_view.html', context)


@user_passes_test(is_member)
def member_view(request):
    """
    View accessible only to users with 'Member' role.
    Displays member-specific content and controls.
    """
    context = {
        'role': 'Member',
        'message': 'Welcome to your Member Dashboard',
        'description': 'You have access to browse library resources and manage your profile.',
    }
    return render(request, 'relationship_app/member_view.html', context)
