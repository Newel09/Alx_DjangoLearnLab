from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Book, CustomUser


class CustomUserAdmin(UserAdmin):
    """Custom admin for CustomUser model."""
    list_display = ("email", "username", "date_of_birth", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "date_of_birth")
    search_fields = ("email", "username")
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "date_of_birth", "profile_photo")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publication_year")
    list_filter = ("author", "publication_year")
    search_fields = ("title", "author")


admin.site.register(CustomUser, CustomUserAdmin)
