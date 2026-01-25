from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from bookshelf.models import CustomUser


class Command(BaseCommand):
    help = 'Create test users and assign them to groups for permission testing'

    def handle(self, *args, **options):
        # Test user credentials
        test_users = [
            {'username': 'viewer_user', 'email': 'viewer@test.com', 'password': 'testpass123', 'group': 'Viewers'},
            {'username': 'editor_user', 'email': 'editor@test.com', 'password': 'testpass123', 'group': 'Editors'},
            {'username': 'admin_user', 'email': 'admin@test.com', 'password': 'testpass123', 'group': 'Admins'},
        ]
        
        for user_data in test_users:
            # Create user
            user, created = CustomUser.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user_data["username"]} (Password: {user_data["password"]})')
                )
            else:
                self.stdout.write(f'User {user_data["username"]} already exists')
            
            # Assign to group
            try:
                group = Group.objects.get(name=user_data['group'])
                user.groups.add(group)
                self.stdout.write(
                    self.style.SUCCESS(f'Assigned {user_data["username"]} to {user_data["group"]} group')
                )
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Group {user_data["group"]} does not exist. Run create_groups command first.')
                )
        
        self.stdout.write(self.style.SUCCESS('\nTest users created successfully!'))
        self.stdout.write('\nTest User Credentials:')
        self.stdout.write('=' * 60)
        for user_data in test_users:
            self.stdout.write(f'Username: {user_data["username"]:20} | Password: {user_data["password"]:15} | Group: {user_data["group"]}')
        self.stdout.write('=' * 60)
