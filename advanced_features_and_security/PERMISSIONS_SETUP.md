# Django Groups and Permissions System - Setup Guide

## Overview

This document outlines the implementation of a role-based access control (RBAC) system using Django's built-in Groups and Permissions framework. The system restricts access to book management operations based on user roles.

---

## System Architecture

### Permission Hierarchy

```
Viewers Group
├── can_view_book
└── Access: View books only

Editors Group
├── can_view_book
├── can_create_book
├── can_edit_book
└── Access: View, create, and edit books

Admins Group
├── can_view_book
├── can_create_book
├── can_edit_book
├── can_delete_book
└── Access: Full book management (view, create, edit, delete)
```

### Custom Permissions Defined

All permissions are defined on the `Book` model in `bookshelf/models.py`:

- **`can_view_book`** - Permission to view/list books
- **`can_create_book`** - Permission to create new books
- **`can_edit_book`** - Permission to modify existing books
- **`can_delete_book`** - Permission to delete books

---

## Setup Instructions

### Step 1: Run Migrations

First, ensure the database schema is up to date:

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates the permission records in the database.

### Step 2: Create Groups and Assign Permissions

Run the management command to create groups and assign permissions:

```bash
python manage.py create_groups
```

This command:
- Creates three groups: `Viewers`, `Editors`, and `Admins`
- Assigns appropriate permissions to each group
- Displays confirmation messages for each group created

### Step 3: Create Test Users (Optional)

For testing purposes, create test users pre-assigned to groups:

```bash
python manage.py create_test_users
```

This creates three test users:
- **viewer_user** (Group: Viewers) - Can only view books
- **editor_user** (Group: Editors) - Can view, create, and edit books
- **admin_user** (Group: Admins) - Full access to all book operations

Each user has password: `testpass123`

---

## Usage

### Assigning Users to Groups

#### Via Django Admin Interface

1. Go to `/admin/`
2. Navigate to **Auth > Groups**
3. Select a group (Viewers, Editors, or Admins)
4. Add users to the group
5. Save

#### Programmatically

```python
from django.contrib.auth.models import Group
from bookshelf.models import CustomUser

user = CustomUser.objects.get(username='username')
group = Group.objects.get(name='Editors')
user.groups.add(group)
```

### Checking Permissions

#### In Views

The views automatically check permissions using the `@permission_required` decorator:

```python
@permission_required('bookshelf.can_view_book', raise_exception=True)
def book_list(request):
    # This view requires can_view_book permission
    pass
```

#### In Templates

Check permissions in templates:

```django
{% if perms.bookshelf.can_edit_book %}
    <a href="{% url 'book-edit' book.id %}">Edit</a>
{% endif %}

{% if perms.bookshelf.can_delete_book %}
    <a href="{% url 'book-delete' book.id %}">Delete</a>
{% endif %}
```

#### Programmatically

```python
if user.has_perm('bookshelf.can_edit_book'):
    # Allow edit operation
    pass
```

---

## View Endpoints and Permissions

| Endpoint | Method | Permission Required | Description |
|----------|--------|-------------------|-------------|
| `/books/` | GET | `can_view_book` | List all books |
| `/books/<id>/` | GET | `can_view_book` | View book details |
| `/books/create/` | GET, POST | `can_create_book` | Create new book |
| `/books/<id>/edit/` | GET, POST | `can_edit_book` | Edit existing book |
| `/books/<id>/delete/` | GET, POST | `can_delete_book` | Delete book |

---

## Testing Checklist

### Test Case 1: Viewers Group
- [ ] Log in as `viewer_user`
- [ ] ✅ Can access `/books/` (list view)
- [ ] ✅ Can access `/books/<id>/` (detail view)
- [ ] ❌ Cannot access `/books/create/` (403 Forbidden)
- [ ] ❌ Cannot access `/books/<id>/edit/` (403 Forbidden)
- [ ] ❌ Cannot access `/books/<id>/delete/` (403 Forbidden)

### Test Case 2: Editors Group
- [ ] Log in as `editor_user`
- [ ] ✅ Can access `/books/` (list view)
- [ ] ✅ Can access `/books/<id>/` (detail view)
- [ ] ✅ Can access `/books/create/` (create view)
- [ ] ✅ Can access `/books/<id>/edit/` (edit view)
- [ ] ❌ Cannot access `/books/<id>/delete/` (403 Forbidden)

### Test Case 3: Admins Group
- [ ] Log in as `admin_user`
- [ ] ✅ Can access `/books/` (list view)
- [ ] ✅ Can access `/books/<id>/` (detail view)
- [ ] ✅ Can access `/books/create/` (create view)
- [ ] ✅ Can access `/books/<id>/edit/` (edit view)
- [ ] ✅ Can access `/books/<id>/delete/` (delete view)

### Test Case 4: Anonymous/Unauthenticated User
- [ ] Attempt to access any endpoint
- [ ] ❌ Should be redirected to login page

---

## Configuration Files Modified

### bookshelf/models.py
- Added custom permissions to the `Book` model
- Defined `can_view_book`, `can_create_book`, `can_edit_book`, `can_delete_book`

### bookshelf/views.py
- Implemented 5 views with `@permission_required` decorators
- Each view enforces its respective permission

### bookshelf/admin.py
- Registered `CustomUser` and `Book` models in Django admin
- `CustomUserAdmin` provides admin interface for user management

### bookshelf/forms.py
- Created `BookForm` for book creation and editing

### bookshelf/urls.py
- Defined URL patterns for all book management endpoints

### bookshelf/management/commands/create_groups.py
- Management command to create groups and assign permissions

### bookshelf/management/commands/create_test_users.py
- Management command to create test users for permission testing

---

## Troubleshooting

### Groups Not Found Error
**Problem**: "Group Viewers does not exist" when creating test users

**Solution**: Run `python manage.py create_groups` first to create the groups

### Permissions Not Available
**Problem**: Custom permissions not showing in admin

**Solution**: Run migrations after adding permissions to models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Users Not Inheriting Group Permissions
**Problem**: User has permission assigned individually but group permissions not working

**Solution**: Users must be explicitly added to groups. Verify in Django admin:
1. Go to Auth > Users
2. Select user
3. Check "Groups" section has the appropriate groups selected

---

## Security Best Practices

1. **Never hardcode permissions** in views - always use `@permission_required`
2. **Check permissions in templates** before displaying sensitive links
3. **Use `raise_exception=True`** to prevent information disclosure
4. **Regularly audit** group memberships
5. **Test permission enforcement** regularly
6. **Use descriptive permission names** that clearly indicate the action

---

## Additional Resources

- [Django Permissions and Authorization](https://docs.djangoproject.com/en/stable/topics/auth/default/)
- [Django Groups Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.models.Group)
- [Permission Required Decorator](https://docs.djangoproject.com/en/stable/topics/auth/default/#django.contrib.auth.decorators.permission_required)

---

## Contact & Support

For questions or issues with the permissions system, refer to the inline code documentation in:
- `bookshelf/views.py` - View-level permission enforcement
- `bookshelf/management/commands/create_groups.py` - Group creation logic
- `bookshelf/management/commands/create_test_users.py` - Test user setup
