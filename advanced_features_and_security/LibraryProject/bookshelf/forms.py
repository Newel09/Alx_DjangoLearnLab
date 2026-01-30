from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    """Form for creating and editing Book instances."""
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name'
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter publication year'
            }),
        }


class ExampleForm(forms.Form):
    """A simple example form used for demonstrations and tests."""

    name = forms.CharField(
        max_length=100,
        label='Your name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
    )
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
    )
    message = forms.CharField(
        label='Message',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Optional message'})
    )
    subscribe = forms.BooleanField(
        label='Subscribe to updates',
        required=False,
        initial=False
    )
