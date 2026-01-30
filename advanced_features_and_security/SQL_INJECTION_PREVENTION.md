# SQL Injection Prevention & Secure Data Access Guide

## Overview

This guide explains how to prevent SQL injection attacks and implement secure data access patterns in Django applications. SQL injection is one of the most dangerous web vulnerabilities, allowing attackers to manipulate database queries and steal/modify data.

---

## What is SQL Injection?

### Attack Scenario (Vulnerable Code)

```python
# ❌ VULNERABLE - DON'T DO THIS!
search_term = request.GET.get('search')
query = f"SELECT * FROM bookshelf_book WHERE title = '{search_term}'"
books = Book.objects.raw(query)
```

If a user enters: `' OR '1'='1`, the query becomes:
```sql
SELECT * FROM bookshelf_book WHERE title = '' OR '1'='1'
```

This returns ALL books, even if they shouldn't be visible!

Worse attack: `'; DROP TABLE bookshelf_book; --`
```sql
SELECT * FROM bookshelf_book WHERE title = ''; DROP TABLE bookshelf_book; --'
```

This **deletes the entire table**!

---

## Django ORM Protection (Safe)

### Safe Database Queries Using ORM

Django's ORM automatically escapes parameters, preventing SQL injection:

```python
# ✅ SAFE - Using Django ORM
search_term = request.GET.get('search', '').strip()
books = Book.objects.filter(title__icontains=search_term)
```

The ORM converts this to parameterized SQL:
```sql
SELECT * FROM bookshelf_book WHERE title ILIKE %s
```
The `search_term` is passed as a parameter, not concatenated into the query.

### Common ORM Query Methods (All Safe)

```python
from django.db.models import Q

# Filter (returns QuerySet)
books = Book.objects.filter(author='John Doe')  # ✅ Safe

# Get single object
book = Book.objects.get(id=1)  # ✅ Safe

# Exclude
books = Book.objects.exclude(publication_year=2020)  # ✅ Safe

# Complex queries with Q objects
books = Book.objects.filter(
    Q(title__icontains='Python') | 
    Q(author__icontains='Guido')
)  # ✅ Safe

# Chained filters
books = Book.objects.filter(
    publication_year__gte=2000
).filter(
    author__startswith='A'
)  # ✅ Safe

# Count
count = Book.objects.filter(publication_year=2024).count()  # ✅ Safe

# Exists
exists = Book.objects.filter(title='Django').exists()  # ✅ Safe
```

### Field Lookup Types (Case-Insensitive Searches)

```python
# All of these are SQL injection safe:

# Exact match
Book.objects.filter(title__exact='Django')

# Case-insensitive exact
Book.objects.filter(title__iexact='django')

# Contains
Book.objects.filter(title__contains='python')

# Case-insensitive contains
Book.objects.filter(title__icontains='python')  # ← Most useful for search

# Starts with
Book.objects.filter(author__startswith='John')

# Case-insensitive starts with
Book.objects.filter(author__istartswith='john')

# Ends with
Book.objects.filter(title__endswith='Guide')

# Greater than / Less than
Book.objects.filter(publication_year__gt=2000)
Book.objects.filter(publication_year__gte=2000)
Book.objects.filter(publication_year__lt=2030)
Book.objects.filter(publication_year__lte=2030)

# In list
Book.objects.filter(id__in=[1, 2, 3])

# Range
Book.objects.filter(publication_year__range=[2000, 2024])
```

---

## Raw SQL (Use Carefully)

If you must use raw SQL, **always use parameter placeholders**:

### ❌ VULNERABLE - String Concatenation

```python
# DON'T DO THIS!
search = request.GET.get('search')
query = f"SELECT * FROM bookshelf_book WHERE title = '{search}'"
books = Book.objects.raw(query)
```

### ✅ SAFE - Parameterized Queries

```python
# SAFE - Use %s placeholders
search = request.GET.get('search', '').strip()
query = "SELECT * FROM bookshelf_book WHERE title ILIKE %s"
books = Book.objects.raw(query, [search])
```

### ✅ SAFE - Named Placeholders (PostgreSQL)

```python
# Named placeholders are more readable
query = "SELECT * FROM bookshelf_book WHERE title ILIKE %(search)s"
books = Book.objects.raw(query, {'search': search})
```

### ✅ SAFE - Using cursor with parameters

```python
from django.db import connection

def search_books(search_term):
    """
    Secure database query using parameterized queries.
    """
    with connection.cursor() as cursor:
        # Use %s placeholders - the value is passed separately
        cursor.execute(
            "SELECT id, title, author FROM bookshelf_book WHERE title ILIKE %s",
            [search_term]  # Passed as parameter, not concatenated
        )
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

# Usage
books = search_books('%python%')  # ✅ Safe
```

---

## Input Validation & Sanitization

### Using Django Forms (Recommended)

```python
from django import forms
from .models import Book

class BookSearchForm(forms.Form):
    """
    Form for searching books.
    Validates and cleans user input automatically.
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by title or author',
            'class': 'form-control'
        })
    )
    publication_year = forms.IntegerField(
        required=False,
        min_value=1000,
        max_value=2100
    )
    
    def clean_search(self):
        """Validate search field"""
        search = self.cleaned_data['search'].strip()
        
        # Remove leading/trailing whitespace
        if search and len(search) < 2:
            raise forms.ValidationError("Search term must be at least 2 characters")
        
        return search
    
    def clean_publication_year(self):
        """Validate year field"""
        year = self.cleaned_data.get('publication_year')
        if year and (year < 1000 or year > 2100):
            raise forms.ValidationError("Invalid year range")
        return year

# In view
def search_books(request):
    """View with input validation"""
    form = BookSearchForm(request.GET)
    
    if form.is_valid():
        search = form.cleaned_data['search']
        year = form.cleaned_data['publication_year']
        
        # Use ORM with validated data
        books = Book.objects.all()
        if search:
            books = books.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search)
            )
        if year:
            books = books.filter(publication_year=year)
        
        return render(request, 'search_results.html', {
            'books': books,
            'form': form
        })
    
    return render(request, 'search.html', {'form': form})
```

### Manual Input Validation

```python
import re

def validate_search_input(search_term):
    """
    Validate search input.
    Note: Django ORM escaping is the primary defense,
    this is additional validation for safety.
    """
    if not search_term:
        return ""
    
    # Remove leading/trailing whitespace
    search_term = search_term.strip()
    
    # Limit length
    if len(search_term) > 200:
        raise ValueError("Search term too long")
    
    # Check for dangerous patterns (optional, ORM handles escaping)
    if any(char in search_term for char in ['<', '>', '"', "'"]):
        # These are harmless in ORM but can log suspicious activity
        log_suspicious_search(search_term)
    
    return search_term

# Usage in view
try:
    search = validate_search_input(request.GET.get('search', ''))
    books = Book.objects.filter(title__icontains=search)
except ValueError as e:
    return render(request, 'error.html', {'error': str(e)})
```

---

## Implementation in Views

### Secure Search View

```python
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.db.models import Q

@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_list(request):
    """
    View to list books with secure search functionality.
    
    Security Features:
    1. ORM queries prevent SQL injection
    2. User input validated and stripped
    3. Permission check enforces access control
    4. Q objects create safe complex queries
    """
    books = Book.objects.all()
    search_query = request.GET.get('search', '').strip()
    
    # Limit search query length
    if len(search_query) > 200:
        search_query = search_query[:200]
    
    # SAFE SEARCH - Using ORM
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    return render(request, 'bookshelf/book_list.html', context)
```

### Get Object Safely

```python
from django.shortcuts import get_object_or_404

@permission_required('bookshelf.can_view_book')
def book_detail(request, pk):
    """
    Safely retrieve a single book.
    
    get_object_or_404 uses parameterized queries:
    - pk is safely escaped
    - Returns 404 if object not found
    - Prevents information disclosure
    """
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})
```

---

## Testing for SQL Injection

### Test Cases

```python
from django.test import TestCase, Client

class SQLInjectionTestCase(TestCase):
    def setUp(self):
        Book.objects.create(
            title='Django for Beginners',
            author='William Vincent',
            publication_year=2021
        )
        self.client = Client()
    
    def test_search_with_sql_injection_attempt(self):
        """
        Test that SQL injection attempts are safely handled.
        """
        # Common SQL injection payloads
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE books; --",
            "1' UNION SELECT * FROM auth_user --",
            "admin'--",
        ]
        
        for payload in payloads:
            response = self.client.get('/books/', {'search': payload})
            # Should return 200 (no error) and not execute injection
            self.assertEqual(response.status_code, 200)
            # Should not contain admin or sensitive data
            self.assertNotIn('admin', response.content.decode())
    
    def test_search_with_valid_input(self):
        """Test legitimate search works"""
        response = self.client.get('/books/', {'search': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django for Beginners')
    
    def test_search_with_special_characters(self):
        """Test search with special characters"""
        response = self.client.get('/books/', {'search': 'C++'})
        self.assertEqual(response.status_code, 200)
```

---

## Security Best Practices

### ✅ DO:
- Always use Django ORM when possible
- Use parameterized queries if raw SQL is needed
- Validate inputs with Django forms
- Limit input length
- Use `get_object_or_404()` for single objects
- Log suspicious search patterns
- Test with SQL injection payloads

### ❌ DON'T:
- Never concatenate user input into SQL queries
- Never use `eval()` or `exec()` with user input
- Never disable Django's automatic escaping
- Never trust user input, even from your own frontend
- Never use user input in raw strings
- Never store sensitive data in plain text

---

## Monitoring and Logging

### Log Suspicious Queries

```python
import logging

logger = logging.getLogger('security')

def log_suspicious_search(search_term):
    """Log searches that look suspicious"""
    if any(keyword in search_term.lower() for keyword in ['drop', 'delete', 'insert', 'union']):
        logger.warning(
            f"Suspicious search pattern detected: {search_term}",
            extra={
                'user': request.user,
                'ip': get_client_ip(request),
            }
        )

def get_client_ip(request):
    """Get client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

## Summary of Safe Patterns

| Pattern | Safety | Speed | Use Case |
|---------|--------|-------|----------|
| `Book.objects.filter()` | ✅ Safe | ⚡ Fast | Most queries |
| `Book.objects.get()` | ✅ Safe | ⚡ Fast | Single objects |
| `Book.objects.raw()` with params | ✅ Safe | ⚡ Fast | Complex SQL |
| `connection.cursor()` with params | ✅ Safe | ⚡ Fast | Advanced queries |
| String concatenation | ❌ Unsafe | 💥 Dangerous | NEVER |
| `.filter(Q() objects)` | ✅ Safe | ⚡ Fast | Complex AND/OR |

---

## Django Security Commands

```bash
# Check for security issues
python manage.py check --deploy

# View raw SQL queries (development only)
python shell
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    books = Book.objects.filter(title__icontains='Django')
    
for query in context:
    print(query['sql'])
```

---

## Additional Resources

- [Django ORM Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Query Expressions](https://docs.djangoproject.com/en/stable/topics/db/queries/)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
