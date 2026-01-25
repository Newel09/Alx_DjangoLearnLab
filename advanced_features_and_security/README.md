# Advanced Features and Security - Custom Django User Model

## Overview

This Django project demonstrates the implementation of a **custom user model** that extends Django's `AbstractUser` class. This implementation showcases advanced Django authentication system customization, allowing applications to define user attributes beyond Django's built-in user model.

## Project Structure

```
advanced_features_and_security/
├── LibraryProject/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── LibraryProject/          # Project configuration
│   │   ├── settings.py          # Contains AUTH_USER_MODEL configuration
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── bookshelf/               # Django app for book management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── migrations/
│   └── relationship_app/         # Main app with custom user model
│       ├── models.py            # Contains CustomUser, CustomUserManager, and other models
│       ├── admin.py             # Custom admin configuration
│       ├── views.py
│       ├── urls.py
│       └── migrations/
```

## Key Features Implemented

### 1. Custom User Manager (`CustomUserManager`)

Located in `relationship_app/models.py`, this manager implements:

- **`create_user(email, password=None, **extra_fields)`**: Creates a regular user with email-based authentication
- **`create_superuser(email, password=None, **extra_fields)`**: Creates a superuser with all necessary permissions

#### Key Features:
- Email validation and normalization
- Secure password handling
- Automatic permission assignment for superusers

```python
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Validates email, normalizes it, sets password, and saves user
        
    def create_superuser(self, email, password=None, **extra_fields):
        # Creates a superuser with is_staff=True and is_superuser=True
```

### 2. Custom User Model (`CustomUser`)

Extends Django's `AbstractUser` to include:

- **`email`** (EmailField, unique): Primary authentication field
- **`date_of_birth`** (DateField, optional): User's birth date
- **`profile_photo`** (ImageField, optional): User's profile picture stored in `profile_photos/` directory

#### Configuration:
- Uses `CustomUserManager` as the default manager
- `USERNAME_FIELD = 'email'` - Email is used for authentication instead of username
- `REQUIRED_FIELDS = ['username']` - Username is still required during creation

```python
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

### 3. Settings Configuration

In `LibraryProject/settings.py`, the custom user model is registered:

```python
# Custom User Model Configuration
AUTH_USER_MODEL = 'relationship_app.CustomUser'
```

This tells Django to use `CustomUser` from the `relationship_app` instead of the default `User` model throughout the entire project.

### 4. Custom Admin Interface

The `CustomUserAdmin` class in `relationship_app/admin.py` provides:

#### List View Display:
- email, username, first_name, last_name, date_of_birth, is_staff, is_active
- Filterable by: is_staff, is_superuser, is_active, date_joined
- Searchable by: email, username, first_name, last_name

#### Edit User Form (fieldsets):
1. **Authentication**: email, username, password
2. **Personal Information**: first_name, last_name, date_of_birth, profile_photo
3. **Permissions** (collapsible): is_active, is_staff, is_superuser, groups, user_permissions
4. **Important Dates** (collapsible): last_login, date_joined

#### Add User Form:
Simplified form with essential fields for creating new users.

### 5. Updated Models

All models have been updated to use the custom user model:

- **`UserProfile`**: Changed from `ForeignKey(User, ...)` to `ForeignKey(CustomUser, ...)`

## Usage Examples

### Creating a Regular User

```python
from relationship_app.models import CustomUser

user = CustomUser.objects.create_user(
    email='john@example.com',
    username='john_doe',
    password='secure_password123',
    first_name='John',
    last_name='Doe',
    date_of_birth='1990-05-15'
)
```

### Creating a Superuser

```python
superuser = CustomUser.objects.create_superuser(
    email='admin@example.com',
    username='admin',
    password='admin_password123'
)
```

### Querying Users

```python
# Get user by email
user = CustomUser.objects.get(email='john@example.com')

# Get all users with birth dates
users_with_dob = CustomUser.objects.exclude(date_of_birth__isnull=True)

# Get user by username
user = CustomUser.objects.get(username='john_doe')
```

### Accessing User Profile Photo

```python
if user.profile_photo:
    photo_url = user.profile_photo.url
```

## Database Migrations

Before running the application, you need to create and apply migrations:

```bash
# Create migrations for the custom user model
python manage.py makemigrations

# Apply migrations to the database
python manage.py migrate
```

**Note:** If you're migrating from a project using Django's default `User` model, you'll need to handle data migration carefully.

## Related Models

The project includes the following models that work with the custom user model:

- **`CustomUser`**: The custom user model (extends AbstractUser)
- **`UserProfile`**: Extended user profile with role-based access control (admin, librarian, member)
- **`Author`**: Represents book authors
- **`Book`**: Represents books with ForeignKey to Author
- **`Library`**: Represents libraries with ManyToMany relationship to Books
- **`Librarian`**: Represents librarians with OneToOne relationship to Library

## Admin Interface Access

1. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

3. Access the admin panel at: `http://localhost:8000/admin/`

## Security Considerations

1. **Email Uniqueness**: The email field is marked as unique, preventing duplicate accounts
2. **Password Security**: Passwords are hashed using Django's password hashing algorithm
3. **Superuser Validation**: The `create_superuser` method ensures proper permission flags are set
4. **Image Upload Security**: Profile photos are stored in a dedicated directory with proper file handling

## Dependencies

To use the profile_photo field (ImageField), you need to install Pillow:

```bash
pip install Pillow
```

## Key Differences from Default User Model

| Aspect | Default User | Custom User |
|--------|--------------|------------|
| Authentication Field | username | email |
| Email Required | No | Yes (unique) |
| Custom Fields | None | date_of_birth, profile_photo |
| Custom Manager | Built-in | CustomUserManager |
| Admin Interface | Generic | Customized with additional fields |

## Best Practices Implemented

1. ✅ Custom user manager handles both regular users and superusers
2. ✅ Email-based authentication for modern user experience
3. ✅ Proper field validation in the manager
4. ✅ Optional custom fields (date_of_birth, profile_photo) with null=True, blank=True
5. ✅ Comprehensive admin interface with proper fieldsets
6. ✅ Proper app_label configuration for multi-app projects
7. ✅ All models updated to reference the new custom user model
8. ✅ Settings.py properly configured with AUTH_USER_MODEL

## Future Enhancements

Possible improvements to this implementation:

- Add phone number field for contact information
- Add address fields (street, city, country, postal_code)
- Implement email verification system
- Add two-factor authentication support
- Add user avatar with thumbnail generation
- Implement social authentication (OAuth)
- Add user preferences/settings model
- Implement user activity logging

## References

- [Django Custom User Model Documentation](https://docs.djangoproject.com/en/stable/topics/auth/customizing/#extending-the-existing-user-model)
- [Django AbstractUser](https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.models.AbstractUser)
- [Django BaseUserManager](https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.models.BaseUserManager)
- [Django UserAdmin](https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.UserAdmin)
