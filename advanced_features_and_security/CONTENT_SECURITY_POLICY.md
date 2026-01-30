# Content Security Policy (CSP) Implementation Guide

## Overview

Content Security Policy (CSP) is a security mechanism that helps prevent Cross-Site Scripting (XSS), clickjacking, and other content-based attacks by allowing you to specify which domains can load content in your application.

---

## What is CSP?

### How CSP Works

CSP works by sending an HTTP header that tells the browser:
- Which domains can load scripts
- Which domains can load stylesheets
- Which domains can load images
- Whether inline scripts are allowed
- Much more...

### CSP Prevents

```
Attack: Injected Script
<img src="x" onerror="alert('XSS')">

With CSP: Script is blocked by browser
Browser console: "Content Security Policy: 
  The page's settings blocked the running of inline scripts (onerror)..."
```

```
Attack: Loading external malicious script
<script src="https://attacker.com/malware.js"></script>

With CSP: Script load is blocked
Browser console: "Content Security Policy: Refused to load the 
  script from 'https://attacker.com/malware.js' because it 
  violates the following directive: script-src 'self'..."
```

---

## CSP Directives

### Primary Directives in Our Configuration

```python
# Default source for all content types
CSP_DEFAULT_SRC = ("'self'",)
# Allows resources only from same origin

# Scripts - Can execute JavaScript
CSP_SCRIPT_SRC = ("'self'",)
# Only scripts from same origin allowed

# Stylesheets - Can load CSS
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
# CSS from same origin + inline styles allowed

# Images - Can load images
CSP_IMG_SRC = ("'self'", "data:")
# Images from same origin and data URIs allowed

# Fonts - Can load web fonts
CSP_FONT_SRC = ("'self'",)
# Fonts from same origin only

# Connections - AJAX, WebSocket, etc.
CSP_CONNECT_SRC = ("'self'",)
# Connections to same origin only

# Frame ancestors - Can embed in frames
CSP_FRAME_ANCESTORS = ("'none'",)
# Cannot be embedded in frames

# Embedded frames/iframes
CSP_FRAME_SRC = ("'self'",)
# Can only embed frames from same origin

# Objects/Embeds - Flash, ActiveX, etc.
CSP_OBJECT_SRC = ("'none'",)
# Disables Flash, plugins completely
```

---

## Configuration Examples

### Strict CSP (Most Secure)

```python
# Maximum restriction - nothing external
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'",)
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FRAME_SRC = ("'none'",)
CSP_OBJECT_SRC = ("'none'",)
```

### Moderate CSP (Balanced)

```python
# Allow some external resources
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://cdn.example.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.example.com")
CSP_IMG_SRC = ("'self'", "data:", "https://cdn.example.com")
CSP_FONT_SRC = ("'self'", "https://fonts.googleapis.com")
CSP_CONNECT_SRC = ("'self'", "https://api.example.com")
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FRAME_SRC = ("'self'",)
CSP_OBJECT_SRC = ("'none'",)
```

### Permissive CSP (Less Restrictive)

```python
# Allow more external content
CSP_DEFAULT_SRC = ("'self'", "https:")
CSP_SCRIPT_SRC = ("'self'", "https:", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "https:", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "https:", "data:")
CSP_FONT_SRC = ("'self'", "https:")
CSP_CONNECT_SRC = ("'self'", "https:")
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_FRAME_SRC = ("'self'", "https:")
CSP_OBJECT_SRC = ("'none'",)
```

---

## CSP Source Values

### Common Source Values

```python
# Self - Same origin only
"'self'"

# Specific domain
"https://example.com"
"https://*.example.com"  # All subdomains

# HTTPS only
"https:"

# Any source (defeats CSP purpose)
"*"

# Inline scripts/styles (not recommended)
"'unsafe-inline'"

# eval() and related (not recommended)
"'unsafe-eval'"

# Nonce for inline scripts (advanced)
"'nonce-{random-value}'"

# Hash of inline script content
"'sha256-{base64-hash}'"

# None - Don't allow any
"'none'"
```

---

## Implementation in Django

### Using CSP Middleware

```python
# settings.py - Django already provides CSP settings
# No additional middleware needed for basic CSP

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
# ... other directives
```

### Installing django-csp (Optional, for advanced features)

```bash
pip install django-csp
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'csp',
]

MIDDLEWARE = [
    # ...
    'csp.middleware.CSPMiddleware',
]

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
# ... configure other directives
```

### Manual CSP Header in Views

```python
from django.http import HttpResponse

def my_view(request):
    response = HttpResponse("Content here")
    
    # Set CSP header manually
    response['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
    
    # Report-only mode (violations logged, not enforced)
    response['Content-Security-Policy-Report-Only'] = "default-src 'self'"
    
    return response
```

---

## Working with Inline Styles and Scripts

### Problem: Inline Styles Blocked by CSP

```django
<!-- This will be blocked if CSP_STYLE_SRC doesn't include 'unsafe-inline' -->
<h1 style="color: red;">Title</h1>

<!-- Error: "Refused to apply inline style" -->
```

### Solution 1: Allow Unsafe-Inline (Less Secure)

```python
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
```

### Solution 2: Use Nonces (Recommended)

```python
# views.py
import secrets
from django.shortcuts import render

def my_view(request):
    # Generate random nonce
    nonce = secrets.token_urlsafe(16)
    
    # Store nonce for template
    context = {
        'nonce': nonce,
    }
    
    # Render response
    response = render(request, 'template.html', context)
    
    # Set CSP header with nonce
    csp_header = f"script-src 'self' 'nonce-{nonce}'; style-src 'self' 'nonce-{nonce}'"
    response['Content-Security-Policy'] = csp_header
    
    return response
```

```django
<!-- template.html -->
<style nonce="{{ nonce }}">
    h1 { color: red; }
</style>

<script nonce="{{ nonce }}">
    console.log('This is allowed with nonce');
</script>
```

### Solution 3: Extract Styles to Separate Files

```django
<!-- Instead of inline -->
<style>
    h1 { color: red; }
</style>

<!-- Use external stylesheet -->
<link rel="stylesheet" href="/static/css/style.css">
```

```python
CSP_STYLE_SRC = ("'self'",)  # No unsafe-inline needed
```

---

## CSP Report-Only Mode (Testing)

### Report Violations Without Blocking

```python
# Test CSP without breaking site
CSP_REPORT_ONLY = True

# Or use specific directive
CSP_REPORT_ONLY_META = {
    'default-src': ("'self'",),
    'script-src': ("'self'",),
}
```

Browser sends violation reports instead of blocking.

### Collect CSP Violation Reports

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["POST"])
def csp_report(request):
    """
    Endpoint to receive CSP violation reports.
    Configure in settings: CSP_REPORT_URI = '/csp-report/'
    """
    try:
        report = json.loads(request.body)
        
        # Log violation
        print(f"CSP Violation: {report}")
        
        # In production, send to logging service or email
        # E.g., Sentry, New Relic, etc.
        
        return JsonResponse({'status': 'received'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# urls.py
urlpatterns = [
    # ...
    path('csp-report/', csp_report, name='csp-report'),
]

# settings.py
CSP_REPORT_URI = '/csp-report/'
```

---

## Debugging CSP Issues

### View CSP Header in Browser

**Chrome/Firefox DevTools:**
1. Press F12 to open Developer Tools
2. Go to Network tab
3. Click on any request
4. Look for response header: `Content-Security-Policy`

### CSP Violations in Console

```javascript
// Browser console shows CSP violations
"Content Security Policy: Refused to load the script 'https://attacker.com/script.js' 
because it violates the following directive: script-src 'self'"
```

### Django Shell Debugging

```bash
python manage.py shell
```

```python
from django.test import Client

client = Client()
response = client.get('/')

# View CSP header
print(response.get('Content-Security-Policy'))
```

---

## Template Security with CSP

### Safe Template Patterns

```django
<!-- ✅ SAFE - No inline scripts -->
<button id="my-button">Click Me</button>

<script src="{% static 'js/button.js' %}"></script>
```

```javascript
// button.js
document.getElementById('my-button').addEventListener('click', function() {
    console.log('Button clicked');
});
```

### Unsafe Patterns (Blocked by CSP)

```django
<!-- ❌ UNSAFE - Inline onclick handler -->
<button onclick="alert('clicked')">Click Me</button>

<!-- ❌ UNSAFE - Inline script tag -->
<script>
    console.log('This will be blocked');
</script>

<!-- ❌ UNSAFE - event attributes -->
<img src="image.jpg" onerror="alert('XSS')">
```

---

## CSP with Django Forms

```django
<!-- ✅ Safe form with CSP -->
<form method="post">
    {% csrf_token %}
    <input type="text" name="search">
    <button type="submit">Search</button>
</form>

<!-- Form submission is allowed - no inline scripts -->

<!-- ✅ Safe form validation -->
<form id="book-form" method="post">
    {% csrf_token %}
    {% for field in form %}
        {{ field.label }}
        {{ field }}
        {% if field.errors %}
            <span class="error">{{ field.errors }}</span>
        {% endif %}
    {% endfor %}
    <button type="submit">Submit</button>
</form>

<!-- Separate validation script file -->
<script src="{% static 'js/form-validation.js' %}"></script>
```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] Review all CSP directives
- [ ] Test in report-only mode first
- [ ] Check browser console for violations
- [ ] Verify all resources load properly
- [ ] Test with different browsers
- [ ] Set up CSP violation reporting

### Deployment Steps

1. **Enable Report-Only Mode**
   ```python
   CSP_REPORT_ONLY = True
   # Deploy and monitor violations
   ```

2. **Analyze Reports**
   - Check violation logs
   - Identify missing directives
   - Fix violations

3. **Enable Enforcement**
   ```python
   CSP_REPORT_ONLY = False
   # Deploy to production
   ```

4. **Monitor**
   - Continue logging violations
   - Adjust as needed

---

## Common CSP Issues and Fixes

### Issue: Google Fonts Not Loading

**Error:** "Refused to load font from 'https://fonts.gstatic.com'"

**Fix:**
```python
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com")
```

### Issue: Analytics Script Blocked

**Error:** "Refused to load script from 'https://www.google-analytics.com'"

**Fix:**
```python
CSP_SCRIPT_SRC = ("'self'", "https://www.google-analytics.com")
CSP_CONNECT_SRC = ("'self'", "https://www.google-analytics.com")
```

### Issue: Bootstrap CDN Not Working

**Error:** "Refused to load stylesheet from 'https://cdn.jsdelivr.net'"

**Fix:**
```python
CSP_STYLE_SRC = ("'self'", "https://cdn.jsdelivr.net")
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net")
```

---

## Testing CSP

### Test Strict CSP

```python
# Test in development
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
# ...

# Load pages and check console for violations
```

### Automated CSP Testing

```bash
# Install CSP validator
pip install csp-checker

# Check CSP headers
python -m csp_checker https://yoursite.com
```

---

## Benefits of CSP

| Threat | CSP Protection |
|--------|---|
| Reflected XSS | ✅ High |
| Stored XSS | ✅ High |
| DOM-based XSS | ✅ Medium |
| Clickjacking | ✅ Partial (with frame-ancestors) |
| Code injection | ✅ Medium |
| Man-in-the-middle | ❌ No (needs HTTPS) |

---

## Summary

1. **CSP restricts** which sources can load content
2. **Prevents XSS** by blocking unsafe scripts
3. **Report violations** to identify issues
4. **Start strict** and relax only when needed
5. **Use nonces** for necessary inline content
6. **Monitor reports** in production
7. **Test thoroughly** before enabling

---

## References

- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Quick Reference](https://content-security-policy.com/)
- [Django CSP Package](https://django-csp.readthedocs.io/)
- [OWASP Content Security Policy](https://owasp.org/www-community/controls/Content_Security_Policy)
