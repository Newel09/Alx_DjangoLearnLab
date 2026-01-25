from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from bookshelf.models import Book


class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **options):
        # Get the Book model's content type
        book_content_type = ContentType.objects.get_for_model(Book)
        
        # Get all custom permissions for Book model
        can_view = Permission.objects.get(
            content_type=book_content_type,
            codename='can_view_book'
        )
        can_create = Permission.objects.get(
            content_type=book_content_type,
            codename='can_create_book'
        )
        can_edit = Permission.objects.get(
            content_type=book_content_type,
            codename='can_edit_book'
        )
        can_delete = Permission.objects.get(
            content_type=book_content_type,
            codename='can_delete_book'
        )
        
        # Create Viewers group
        viewers_group, created = Group.objects.get_or_create(name='Viewers')
        if created:
            viewers_group.permissions.add(can_view)
            self.stdout.write(self.style.SUCCESS('Created group "Viewers" with can_view permission'))
        else:
            self.stdout.write('Group "Viewers" already exists')
        
        # Create Editors group
        editors_group, created = Group.objects.get_or_create(name='Editors')
        if created:
            editors_group.permissions.add(can_view, can_create, can_edit)
            self.stdout.write(self.style.SUCCESS('Created group "Editors" with can_view, can_create, and can_edit permissions'))
        else:
            self.stdout.write('Group "Editors" already exists')
        
        # Create Admins group
        admins_group, created = Group.objects.get_or_create(name='Admins')
        if created:
            admins_group.permissions.add(can_view, can_create, can_edit, can_delete)
            self.stdout.write(self.style.SUCCESS('Created group "Admins" with all permissions'))
        else:
            self.stdout.write('Group "Admins" already exists')
        
        self.stdout.write(self.style.SUCCESS('Groups and permissions setup complete!'))
