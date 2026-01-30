# CSRF Token Protection Implementation Guide

## Overview

This guide explains the implementation of CSRF (Cross-Site Request Forgery) token protection in Django forms and templates. CSRF tokens are essential security measures that prevent unauthorized form submissions from malicious third-party sites.

---

## What is CSRF?

### Attack Scenario

A user logs into your banking website, then visits a malicious website in another tab. That malicious site could:

```html
<!-- Malicious website's hidden form -->
<form action="https://yourbank.com/transfer" method="POST" style="display:none;">
    <input name="account" value="attacker_account">
    <input name="amount" value="10000">
</form>
<script>
    document.forms[0].submit(); // Automatically submit without user knowing
</script>
```

Since the user is still logged in to the bank, their cookies are sent with the request, and the transfer happens without authorization!

### CSRF Token Solution

Django's CSRF token prevents this by:
1. **Generating** a unique token per form/user session
2. **Including** the token in every form
3. **Validating** the token matches when form is submitted
4. **Rejecting** requests without valid tokens

---

## Implementation

### Basic CSRF Token in Forms

```django
<form method="post" action="/submit/">
    {% csrf_token %}
    <input type="text" name="field" required>
    <button type="submit">Submit</button>
</form>
```

The `{% csrf_token %}` template tag renders as:
```html
<input type="hidden" name="csrfmiddlewaretoken" value="abc123def456...">
```

### CSRF in File Upload Forms

```django
<form method="post" action="/upload/" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="document" required>
    <button type="submit">Upload</button>
</form>
```

### CSRF with Django Forms

When using Django's form classes, CSRF token is **automatically included**:

```python
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']

# In template - automatically includes csrf_token
<form method="post">
    {{ form.as_p }}
    <button type="submit">Save</button>
</form>

# Renders with CSRF protection automatically
```

---

## AJAX Requests with CSRF

### Getting CSRF Token from Cookie

```javascript
function getCsrfToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            csrfToken = decodeURIComponent(value);
            break;
        }
    }
    return csrfToken;
}
```

### Fetch API with CSRF Token

```javascript
const csrfToken = getCsrfToken();

fetch('/api/books/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        title: 'New Book',
        author: 'John Doe',
        publication_year: 2024
    })
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

### jQuery with CSRF Token

```javascript
// jQuery automatically handles CSRF for same-domain requests
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:/.test(settings.url) || /^https:/.test(settings.url))) {
            // Only for relative URLs
            xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
        }
    }
});

$.post('/api/books/', {
    title: 'New Book',
    author: 'John Doe',
    publication_year: 2024
}, function(data) {
    console.log('Book created:', data);
});
```

---

## CSRF Configuration in Django

### Middleware (Required)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # ← CSRF Middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

### Template Context Processor

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... other processors ...
                'django.template.context_processors.csrf',  # ← Enables CSRF token
            ],
        },
    },
]
```

### Settings Configuration

```python
# Cookie security (for CSRF token cookie)
CSRF_COOKIE_SECURE = True      # Only send over HTTPS (production)
CSRF_COOKIE_HTTPONLY = False   # Allow JS to read CSRF token (required for AJAX)
CSRF_TRUSTED_ORIGINS = ['https://example.com']  # Trust requests from these origins
```

---

## Template Examples

### Book Creation Form

```django
{% extends 'base.html' %}

{% block content %}
<form method="post">
    {% csrf_token %}  <!-- Required for POST -->
    
    <label>Title:</label>
    <input type="text" name="title" required>
    
    <label>Author:</label>
    <input type="text" name="author" required>
    
    <label>Year:</label>
    <input type="number" name="publication_year" required>
    
    <button type="submit">Create Book</button>
</form>
{% endblock %}
```

### Book Delete Confirmation

```django
{% extends 'base.html' %}

{% block content %}
<h2>Delete: {{ book.title }}</h2>
<p>Are you sure? This cannot be undone.</p>

<form method="post">
    {% csrf_token %}  <!-- Required for DELETE POST -->
    <button type="submit" class="btn-danger">Yes, Delete</button>
</form>
{% endblock %}
```

### Multipart Form (File Upload)

```django
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}  <!-- Still required for file uploads -->
    
    <label>Upload Document:</label>
    <input type="file" name="document" accept=".pdf,.doc,.docx">
    
    <label>Description:</label>
    <textarea name="description"></textarea>
    
    <button type="submit">Upload</button>
</form>
```

---

## View Examples

### Form Processing with CSRF

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_http_methods

@permission_required('bookshelf.can_create_book', raise_exception=True)
@require_http_methods(["GET", "POST"])
def book_create(request):
    """
    CSRF Protection:
    - The @require_http_methods decorator restricts to specific methods
    - Django automatically validates CSRF token for POST requests
    - If token is missing or invalid, 403 Forbidden is raised
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm()
    
    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'action': 'Create'
    })
```

### Manual CSRF Validation in AJAX Views

```python
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

@ensure_csrf_cookie  # Ensures CSRF cookie is set for GET requests
def get_csrf_token(request):
    """
    Endpoint to get CSRF token for frontend AJAX requests.
    This ensures the CSRF cookie is set in the response.
    """
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

@csrf_protect  # Validates CSRF token for POST requests
@require_http_methods(["POST"])
def create_book_api(request):
    """
    API endpoint for book creation with CSRF protection.
    The @csrf_protect decorator validates the CSRF token.
    """
    import json
    try:
        data = json.loads(request.body)
        book = Book.objects.create(
            title=data['title'],
            author=data['author'],
            publication_year=data['publication_year']
        )
        return JsonResponse({'id': book.id, 'message': 'Book created'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
```

---

## Exempting Views from CSRF (Use with Caution!)

In rare cases where you need to disable CSRF protection (e.g., receiving webhooks from external services):

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # ⚠️ Use only for good reason (webhooks, external APIs)
@require_http_methods(["POST"])
def webhook_handler(request):
    """
    This endpoint doesn't require CSRF token.
    Only use for:
    - External webhook endpoints
    - Mobile app API endpoints (with alternative auth)
    - Third-party service integrations
    
    ALWAYS have alternative security measures!
    """
    # Process webhook...
    return JsonResponse({'status': 'success'})
```

---

## Common CSRF Errors

### Error: "403 Forbidden - CSRF token missing or incorrect"

**Causes:**
1. Missing `{% csrf_token %}` in form
2. CSRF middleware not installed
3. Template context processor not configured
4. Token validation failed

**Solution:**
```django
<form method="post">
    {% csrf_token %}  <!-- Add this -->
    <!-- form fields -->
</form>
```

### Error: "403 Forbidden" on AJAX POST

**Cause:** Missing CSRF token header in AJAX request

**Solution:**
```javascript
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCsrfToken(),  // Add this
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

---

## Security Best Practices

### ✅ DO:
- Always include `{% csrf_token %}` in POST/PUT/DELETE forms
- Include CSRF token in AJAX request headers
- Keep CSRF token generation enabled (default)
- Validate tokens on the server side (automatic with middleware)
- Use HTTPS in production to protect token transmission

### ❌ DON'T:
- Don't disable CSRF protection globally
- Don't make CSRF tokens available to untrusted origins
- Don't expose CSRF tokens in URLs or logs
- Don't use `csrf_exempt` without careful consideration
- Don't trust CSRF token alone (use with authentication)

---

## Testing CSRF Protection

### Test Case: Form Without CSRF Token

```python
from django.test import Client, TestCase
from django.contrib.auth.models import User

class CSRFProtectionTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user('testuser', password='pass')
        self.client.login(username='testuser', password='pass')
    
    def test_post_without_csrf_token_rejected(self):
        """POST without CSRF token should be rejected"""
        response = self.client.post('/books/create/', {
            'title': 'Test Book',
            'author': 'Test Author',
            'publication_year': 2024
        })
        # Should get 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_post_with_csrf_token_accepted(self):
        """POST with valid CSRF token should be accepted"""
        # Get CSRF token
        response = self.client.get('/books/create/')
        csrftoken = response.cookies['csrftoken'].value
        
        # POST with token
        response = self.client.post('/books/create/', {
            'title': 'Test Book',
            'author': 'Test Author',
            'publication_year': 2024
        }, HTTP_X_CSRFTOKEN=csrftoken)
        # Should succeed (200 or redirect)
        self.assertIn(response.status_code, [200, 302])
```

---

## Summary

| Component | Purpose | Example |
|-----------|---------|---------|
| `{% csrf_token %}` | Template tag to render token | `<form method="post">{% csrf_token %}</form>` |
| `CsrfViewMiddleware` | Validates tokens | Middleware in INSTALLED_APPS |
| `X-CSRFToken` header | AJAX token header | `headers: {'X-CSRFToken': token}` |
| `csrf_protect` | Decorator for views | `@csrf_protect` |
| `csrf_exempt` | Disable protection | `@csrf_exempt` (use rarely) |
| `get_token()` | Get token in view | `token = get_token(request)` |

---

## References

- [Django CSRF Protection Documentation](https://docs.djangoproject.com/en/stable/ref/csrf/)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Django Security Middleware](https://docs.djangoproject.com/en/stable/ref/middleware/#security-middleware)
