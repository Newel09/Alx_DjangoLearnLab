# Django Security Best Practices - Implementation Guide

## Overview

This document outlines the security measures implemented in the LibraryProject Django application to protect against common web vulnerabilities including XSS, CSRF, SQL injection, and other attacks.

---

## Security Settings Configuration

### 1. DEBUG Mode
```python
DEBUG = True  # Set to False in production
```
- **Purpose**: Prevents detailed error pages from exposing sensitive information
- **Production**: Must be set to `False` in production environments
- **Why**: Debug mode shows database queries, configuration details, and stack traces

### 2. ALLOWED_HOSTS
```python
ALLOWED_HOSTS = ['*']  # Change to specific hosts in production
```
- **Purpose**: Prevents Host Header injection attacks
- **Production Example**: `ALLOWED_HOSTS = ['example.com', 'www.example.com']`
- **Why**: Restricts requests to known domain names only

---

## XSS (Cross-Site Scripting) Protection

### Setting: `SECURE_BROWSER_XSS_FILTER`
```python
SECURE_BROWSER_XSS_FILTER = True
```
- **What it does**: Enables the `X-XSS-Protection` header
- **Browser support**: Tells browsers to enable their built-in XSS filter
- **Protection**: Prevents reflected XSS attacks
- **Example attack blocked**: `<script>alert('XSS')</script>` in URL parameters

### Setting: `SECURE_CONTENT_TYPE_NOSNIFF`
```python
SECURE_CONTENT_TYPE_NOSNIFF = True
```
- **What it does**: Sets `X-Content-Type-Options: nosniff` header
- **Protection**: Prevents MIME type sniffing attacks
- **Example**: Prevents a `.txt` file from being executed as JavaScript

### Implementation in Templates
```django
{% comment %} Always escape user input in templates {% endcomment %}
<p>{{ user_comment }}</p>

{% comment %} Use the |escape filter for extra safety {% endcomment %}
<p>{{ user_input|escape }}</p>

{% comment %} Use safe filter only for trusted content {% endcomment %}
<div>{{ trusted_html_content|safe }}</div>
```

### Auto-escaping
Django templates **auto-escape** HTML special characters by default:
- `<` becomes `&lt;`
- `>` becomes `&gt;`
- `"` becomes `&quot;`
- `'` becomes `&#x27;`

This prevents injected scripts from being interpreted.

---

## Clickjacking Protection

### Setting: `X_FRAME_OPTIONS`
```python
X_FRAME_OPTIONS = 'DENY'
```
- **Options**:
  - `'DENY'` - Page cannot be displayed in a frame (recommended)
  - `'SAMEORIGIN'` - Page can only be framed by pages from same origin
  - `'ALLOW-FROM https://example.com'` - Legacy option (deprecated)
- **What it prevents**: Clickjacking attacks where site is embedded in invisible iframe
- **Example attack blocked**: Embedding your site in a malicious iframe
- **Recommendation**: Use `'DENY'` unless you specifically need framing

---

## CSRF (Cross-Site Request Forgery) Protection

### Setting: `CSRF_COOKIE_SECURE`
```python
CSRF_COOKIE_SECURE = True  # Only in production with HTTPS
CSRF_COOKIE_SECURE = False # In development with HTTP
```
- **Purpose**: Ensures CSRF cookie is only sent over HTTPS
- **Protection**: Prevents cookie interception via man-in-the-middle attacks
- **Production**: Must be `True` when using HTTPS

### Setting: `CSRF_COOKIE_HTTPONLY`
```python
CSRF_COOKIE_HTTPONLY = False
```
- **Why False**: JavaScript needs access to CSRF token in forms
- **Note**: This is intentionally different from session cookies

### CSRF Token in Forms
```django
<form method="post" action="/books/create/">
    {% csrf_token %}
    <input type="text" name="title" required>
    <button type="submit">Create Book</button>
</form>
```
- **`{% csrf_token %}`**: Django template tag that inserts hidden CSRF token
- **Requirement**: All POST, PUT, DELETE requests must include CSRF token
- **Automatic in Django forms**: `django.forms.Form` automatically includes token

### CSRF Token in AJAX Requests
```javascript
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Include in AJAX request header
const csrftoken = getCookie('csrftoken');
fetch('/api/books/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title: 'New Book' })
});
```

---

## Session Cookie Security

### Setting: `SESSION_COOKIE_SECURE`
```python
SESSION_COOKIE_SECURE = True  # Only in production with HTTPS
SESSION_COOKIE_SECURE = False # In development with HTTP
```
- **Purpose**: Ensures session cookie is only sent over HTTPS
- **Protection**: Prevents session hijacking via unencrypted connections
- **Production**: Must be `True` when using HTTPS

### Setting: `SESSION_COOKIE_HTTPONLY`
```python
SESSION_COOKIE_HTTPONLY = True
```
- **Purpose**: Prevents JavaScript from accessing session cookies
- **Protection**: Mitigates XSS attacks that attempt to steal session tokens
- **Note**: Always set to `True` for security

### Setting: `SESSION_COOKIE_AGE`
```python
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
```
- **Purpose**: Defines session timeout duration
- **Default**: 2 weeks (1209600 seconds)
- **Production**: Consider shorter timeouts for sensitive applications

---

## HTTPS and SSL/TLS Protection

### Setting: `SECURE_SSL_REDIRECT`
```python
SECURE_SSL_REDIRECT = True  # In production only
SECURE_SSL_REDIRECT = False # In development
```
- **Purpose**: Automatically redirects HTTP to HTTPS
- **Protection**: Ensures all traffic is encrypted
- **Production**: Must be `True` when using HTTPS

### Setting: `SECURE_HSTS_SECONDS`
```python
SECURE_HSTS_SECONDS = 31536000  # 1 year in seconds
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```
- **What it does**: Sets `Strict-Transport-Security` HTTP header
- **HSTS**: HTTP Strict Transport Security
- **Protection**: Tells browsers to always use HTTPS for your domain
- **Benefits**: Protects against SSL/TLS downgrade attacks
- **Note**: Only enable in production when HTTPS is fully implemented

---

## SQL Injection Prevention

### ORM Query Protection
Django's ORM automatically prevents SQL injection:

**✅ SAFE - Using ORM:**
```python
from bookshelf.models import Book

# Safe: Parameters are escaped
book = Book.objects.get(title='The Great Gatsby')
books = Book.objects.filter(author='F. Scott Fitzgerald')
```

**❌ UNSAFE - Raw SQL:**
```python
# Vulnerable to SQL injection
query = f"SELECT * FROM bookshelf_book WHERE title = '{user_input}'"
Book.objects.raw(query)
```

**✅ SAFE - Parameterized Raw SQL:**
```python
# Safe: Parameters are properly escaped
query = "SELECT * FROM bookshelf_book WHERE title = %s"
Book.objects.raw(query, [user_input])
```

### Best Practices:
- Always use Django ORM (QuerySet) when possible
- If using raw SQL, use parameter placeholders (`%s`)
- Never concatenate user input into SQL queries
- Use `.filter()`, `.get()`, `.exclude()` for queries

---

## Password Security

### Setting: `PASSWORD_HASHERS`
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Primary (default)
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Modern
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # Alternative
]
```
- **First hasher**: Used for new passwords and password changes
- **Other hashers**: Used to verify old passwords (backwards compatibility)
- **PBKDF2**: Default, NIST-approved, works everywhere
- **Argon2**: Modern, memory-hard, resistant to GPU attacks
- **Bcrypt**: Battle-tested, widely used

### Password Validation
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```
- **UserAttributeSimilarityValidator**: Ensures password isn't too similar to username/email
- **MinimumLengthValidator**: Enforces minimum length (default: 8 characters)
- **CommonPasswordValidator**: Rejects common passwords
- **NumericPasswordValidator**: Rejects all-numeric passwords

---

## Input Validation and Sanitization

### Views Example
```python
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q

@permission_required('bookshelf.can_create_book', raise_exception=True)
@require_http_methods(["POST"])
def book_create(request):
    """
    Securely create a new book.
    - Validates form input
    - Checks user permissions
    - Prevents unauthorized access
    """
    form = BookForm(request.POST)
    if form.is_valid():
        # Form validation prevents invalid input
        book = form.save()
        return redirect('book-detail', pk=book.pk)
    return render(request, 'bookshelf/book_form.html', {'form': form})
```

### Form Validation
```python
from django import forms
from bookshelf.models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        
    def clean_title(self):
        """Custom validation for title field"""
        title = self.cleaned_data['title']
        # Prevent XSS by checking for script tags (Django escapes automatically)
        if len(title) > 200:
            raise forms.ValidationError("Title is too long")
        return title
    
    def clean_publication_year(self):
        """Validate publication year"""
        year = self.cleaned_data['publication_year']
        if year < 1000 or year > 2100:
            raise forms.ValidationError("Invalid publication year")
        return year
```

---

## Authentication Security

### Permission Decorators
```python
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='login')
def user_profile(request):
    """Requires user to be logged in"""
    pass

@permission_required('bookshelf.can_delete_book', raise_exception=True)
def book_delete(request, pk):
    """Requires specific permission"""
    pass
```

### Checking Permissions in Views
```python
if request.user.has_perm('bookshelf.can_edit_book'):
    # Allow edit operation
    pass

if request.user.groups.filter(name='Admins').exists():
    # User is in Admins group
    pass
```

---

## Development vs Production Checklist

### Development Settings
```python
DEBUG = True
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
ALLOWED_HOSTS = ['*']
```

### Production Settings
```python
DEBUG = False
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

---

## Security Testing Checklist

- [ ] Run `python manage.py check --deploy` to verify production readiness
- [ ] Test all forms with invalid/malicious input
- [ ] Verify CSRF tokens are present in all POST forms
- [ ] Test permission decorators block unauthorized access
- [ ] Verify cookies have correct security flags (Secure, HttpOnly, SameSite)
- [ ] Check that DEBUG = False in production
- [ ] Verify HTTPS is enforced
- [ ] Test password complexity requirements
- [ ] Verify auto-escaping in templates
- [ ] Test authentication and logout flows

---

## Additional Security Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10 Web Application Risks](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)

---

## Summary of Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `X-XSS-Protection` | `1; mode=block` | Enable browser XSS filter |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Strict-Transport-Security` | `max-age=31536000` | Enforce HTTPS |
| `Set-Cookie` | `Secure; HttpOnly; SameSite=Strict` | Secure cookie transmission |

---

## Quick Production Deployment Checklist

1. Set `DEBUG = False`
2. Update `SECRET_KEY` to a strong random value
3. Configure `ALLOWED_HOSTS` with your domain
4. Set up HTTPS with valid SSL certificate
5. Set `CSRF_COOKIE_SECURE = True`
6. Set `SESSION_COOKIE_SECURE = True`
7. Set `SECURE_SSL_REDIRECT = True`
8. Configure `SECURE_HSTS_SECONDS`
9. Run `python manage.py check --deploy`
10. Review logs for security warnings
11. Implement rate limiting for APIs
12. Set up monitoring and alerts
