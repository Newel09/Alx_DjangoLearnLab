# Custom User Model - Code Examples & Best Practices

## Table of Contents
1. [Creating Users](#creating-users)
2. [Querying Users](#querying-users)
3. [Admin Management](#admin-management)
4. [Authentication](#authentication)
5. [Best Practices](#best-practices)
6. [Common Pitfalls](#common-pitfalls)

---

## Creating Users

### Example 1: Create Regular User with All Fields

```python
from relationship_app.models import CustomUser

user = CustomUser.objects.create_user(
    email='john.doe@example.com',
    username='john_doe',
    password='SecurePassword123!',
    first_name='John',
    last_name='Doe',
    date_of_birth='1990-05-15'
)

print(f"User created: {user.email}")
```

### Example 2: Create User with Profile Photo

```python
from relationship_app.models import CustomUser
from django.core.files.base import ContentFile
import os

user = CustomUser.objects.create_user(
    email='jane@example.com',
    username='jane_smith',
    password='SecurePassword456!'
)

# Add profile photo
photo_path = 'path/to/photo.jpg'
with open(photo_path, 'rb') as f:
    user.profile_photo.save('jane_profile.jpg', ContentFile(f.read()))

user.save()
```

### Example 3: Create Superuser Programmatically

```python
from relationship_app.models import CustomUser

admin = CustomUser.objects.create_superuser(
    email='admin@example.com',
    username='admin_user',
    password='AdminPassword123!'
)

print(f"Superuser created: {admin.email}")
print(f"Is Staff: {admin.is_staff}")
print(f"Is Superuser: {admin.is_superuser}")
```

### Example 4: Using Django Shell

```bash
python manage.py shell
```

```python
from relationship_app.models import CustomUser

# Create user
user = CustomUser.objects.create_user(
    email='test@example.com',
    username='testuser',
    password='TestPass123!'
)

# Update fields
user.date_of_birth = '1995-03-20'
user.save()

# Verify
print(user)  # Output: test@example.com (Test )
```

---

## Querying Users

### Example 1: Get User by Email

```python
from relationship_app.models import CustomUser

try:
    user = CustomUser.objects.get(email='john.doe@example.com')
    print(f"Found: {user.get_full_name()}")
except CustomUser.DoesNotExist:
    print("User not found")
```

### Example 2: Get User by Username

```python
user = CustomUser.objects.get(username='john_doe')
print(f"Email: {user.email}")
```

### Example 3: Filter Users by Date of Birth

```python
from datetime import date

# Users born before 2000
old_users = CustomUser.objects.filter(
    date_of_birth__lt='2000-01-01'
)

# Users with birth date set
users_with_dob = CustomUser.objects.exclude(
    date_of_birth__isnull=True
)

print(f"Users with birth dates: {users_with_dob.count()}")
```

### Example 4: Get Users with Profile Photos

```python
# Users who have uploaded a profile photo
users_with_photos = CustomUser.objects.exclude(
    profile_photo=''
).filter(is_active=True)

for user in users_with_photos:
    print(f"{user.email} - {user.profile_photo.url}")
```

### Example 5: Search Users

```python
from django.db.models import Q

# Search by email or username
search_results = CustomUser.objects.filter(
    Q(email__icontains='example') | Q(username__icontains='john')
)

for user in search_results:
    print(f"{user.email} - {user.username}")
```

### Example 6: Get Staff Members

```python
staff_members = CustomUser.objects.filter(is_staff=True)
print(f"Number of staff: {staff_members.count()}")
```

### Example 7: Get Active Users

```python
active_users = CustomUser.objects.filter(is_active=True)
print(f"Active users: {active_users.count()}")
```

---

## Admin Management

### Accessing Admin Interface

1. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

2. **Navigate to Admin Panel**:
   ```
   http://localhost:8000/admin/
   ```

3. **Login with Superuser Credentials**

### Bulk User Creation in Admin

Users can be created individually through the Django admin interface:

1. Click "Add Custom User"
2. Enter email, username, and password
3. Click "Save and Continue Editing"
4. Add personal information (date of birth, profile photo)
5. Set permissions if needed
6. Save

### Admin Actions

#### Activate/Deactivate Users

```python
from relationship_app.models import CustomUser
from django.contrib import admin

@admin.action(description="Activate selected users")
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)

class CustomUserAdmin(admin.ModelAdmin):
    actions = [activate_users, deactivate_users]
```

---

## Authentication

### Example 1: Authenticate User with Email

```python
from django.contrib.auth import authenticate, login

def login_view(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'login.html', {'error': 'Invalid credentials'})
```

### Example 2: Change User Password

```python
from django.contrib.auth.hashers import make_password

# In a view
user = request.user
user.set_password('NewPassword123!')
user.save()
```

### Example 3: Check User Permissions

```python
if user.is_superuser:
    # Allow all actions
    pass
elif user.is_staff:
    # Allow staff actions
    pass
else:
    # Regular user
    pass
```

### Example 4: Check if User Has Permission

```python
# Check specific permission
if user.has_perm('relationship_app.add_book'):
    # User can add books
    pass

# Check object-level permission
if user.userprofile.role == 'librarian':
    # User is a librarian
    pass
```

---

## Best Practices

### 1. Always Use Email for Authentication

```python
# ✅ Good
user = CustomUser.objects.get(email='user@example.com')

# ❌ Avoid relying only on username when possible
```

### 2. Validate Email Before Creating User

```python
# ✅ Good
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

email = request.POST.get('email')
validator = EmailValidator()

try:
    validator(email)
    user = CustomUser.objects.create_user(email=email, ...)
except ValidationError:
    return render(request, 'error.html', {'error': 'Invalid email'})
```

### 3. Use get_object_or_404 for Safety

```python
from django.shortcuts import get_object_or_404
from relationship_app.models import CustomUser

# ✅ Good - handles 404 automatically
user = get_object_or_404(CustomUser, email='test@example.com')

# ❌ Less safe
try:
    user = CustomUser.objects.get(email='test@example.com')
except CustomUser.DoesNotExist:
    # Handle error
    pass
```

### 4. Use Manager Methods for User Creation

```python
# ✅ Good - uses custom manager
user = CustomUser.objects.create_user(email='user@example.com', ...)

# ❌ Avoid - doesn't hash password
user = CustomUser(email='user@example.com', password='plain_password')
user.save()
```

### 5. Handle Image Upload Safely

```python
from django.core.files.storage import default_storage
import os

# ✅ Good - handles file properly
if request.FILES.get('profile_photo'):
    user.profile_photo = request.FILES['profile_photo']
    user.save()

# Validate file size
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

if request.FILES['profile_photo'].size > MAX_UPLOAD_SIZE:
    return render(request, 'error.html', {'error': 'File too large'})
```

### 6. Use Transactions for Critical Operations

```python
from django.db import transaction

# ✅ Good - atomic operation
@transaction.atomic
def create_user_with_profile(email, username, password):
    user = CustomUser.objects.create_user(
        email=email,
        username=username,
        password=password
    )
    
    from relationship_app.models import UserProfile
    UserProfile.objects.create(
        user=user,
        role='member'
    )
    
    return user
```

### 7. Use Queryset Methods Efficiently

```python
# ✅ Good - efficient
users = CustomUser.objects.filter(
    is_active=True
).values_list('email', flat=True)[:10]

# ❌ Inefficient - loads all users in memory
users = [u.email for u in CustomUser.objects.all()[:10]]
```

---

## Common Pitfalls

### Pitfall 1: Not Setting USERNAME_FIELD

```python
# ❌ Bad - won't work as expected
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    # Forgot to set USERNAME_FIELD = 'email'

# ✅ Good
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

### Pitfall 2: Forgetting to Set AUTH_USER_MODEL

```python
# ❌ Bad - Django still uses default User model
# settings.py (missing or wrong configuration)

# ✅ Good
# settings.py
AUTH_USER_MODEL = 'relationship_app.CustomUser'
```

### Pitfall 3: Using User Import from Old Migration

```python
# ❌ Bad - after switching to CustomUser
from django.contrib.auth.models import User

class OldModel(models.Model):
    user = models.ForeignKey(User, ...)  # Wrong reference

# ✅ Good
from relationship_app.models import CustomUser

class NewModel(models.Model):
    user = models.ForeignKey(CustomUser, ...)
```

### Pitfall 4: Not Handling Database Migration Properly

```bash
# ❌ Bad - might lose data
python manage.py migrate --fake-initial

# ✅ Good - proper migration
python manage.py makemigrations
python manage.py migrate
```

### Pitfall 5: Storing Plain Text Passwords

```python
# ❌ Bad - security risk
user.password = 'plaintext_password'
user.save()

# ✅ Good - use set_password
user.set_password('plaintext_password')
user.save()
```

### Pitfall 6: Not Validating Date of Birth

```python
# ❌ Bad - no validation
user.date_of_birth = request.POST.get('dob')

# ✅ Good - validate date
from datetime import date
from django.core.exceptions import ValidationError

dob_str = request.POST.get('dob')
try:
    dob = date.fromisoformat(dob_str)
    if dob > date.today():
        raise ValidationError("Birth date cannot be in the future")
    user.date_of_birth = dob
except ValueError:
    raise ValidationError("Invalid date format")
```

### Pitfall 7: Uploading Files Without Size Limit

```python
# ❌ Bad - could cause server issues
user.profile_photo = request.FILES['photo']

# ✅ Good - check file size
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB

if request.FILES['photo'].size > MAX_PHOTO_SIZE:
    raise ValidationError("File is too large")

user.profile_photo = request.FILES['photo']
```

---

## Testing Example

```python
from django.test import TestCase
from relationship_app.models import CustomUser

class CustomUserTestCase(TestCase):
    
    def setUp(self):
        """Create test user"""
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
    
    def test_user_creation(self):
        """Test that user is created correctly"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('TestPassword123!'))
    
    def test_superuser_creation(self):
        """Test that superuser is created correctly"""
        admin = CustomUser.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='AdminPass123!'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
    
    def test_unique_email(self):
        """Test that email must be unique"""
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                email='test@example.com',
                username='another_user',
                password='Password123!'
            )
```

---

## Conclusion

The custom user model provides flexibility while maintaining Django's security standards. Follow these examples and best practices to build robust authentication systems.
