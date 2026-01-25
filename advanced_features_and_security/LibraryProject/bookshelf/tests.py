"""
Security Testing Suite for LibraryProject

This module contains comprehensive security tests to verify that:
1. CSRF tokens are required for all POST requests
2. Inputs are properly validated and escaped
3. Permissions are enforced on all views
4. SQL injection attempts are handled safely
5. Security headers are properly set
6. XSS attacks are prevented through template auto-escaping

To run tests:
    python manage.py test bookshelf.tests

To run specific test:
    python manage.py test bookshelf.tests.CSRFProtectionTests

To run with verbose output:
    python manage.py test bookshelf.tests -v 2
"""

from django.test import TestCase, Client
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from bookshelf.models import Book, CustomUser
from django.urls import reverse


class CSRFProtectionTests(TestCase):
    """
    Tests to verify CSRF (Cross-Site Request Forgery) protection is working.
    
    CSRF attacks occur when a malicious site tricks a logged-in user into
    making unauthorized requests. Django prevents this with CSRF tokens.
    """
    
    def setUp(self):
        """Set up test client and user"""
        # Enable CSRF checking
        self.client = Client(enforce_csrf_checks=True)
        
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Add user to Editors group (has can_create_book permission)
        editors_group = Group.objects.create(name='Editors')
        content_type = ContentType.objects.get_for_model(Book)
        permission = Permission.objects.get(
            content_type=content_type,
            codename='can_create_book'
        )
        editors_group.permissions.add(permission)
        self.user.groups.add(editors_group)
    
    def test_post_without_csrf_token_rejected(self):
        """
        Test that POST requests without CSRF token are rejected with 403.
        This is the primary CSRF protection mechanism.
        """
        self.client.login(username='testuser', password='testpass123')
        
        # POST without CSRF token should fail
        response = self.client.post(reverse('book-create'), {
            'title': 'Test Book',
            'author': 'Test Author',
            'publication_year': 2024
        })
        
        # Should get 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_get_csrf_token_from_form(self):
        """
        Test that we can get a CSRF token from the form page.
        """
        self.client.login(username='testuser', password='testpass123')
        
        # GET the form page
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 200)
        
        # Should have CSRF token in response
        self.assertIn('csrfmiddlewaretoken', response.content.decode())
    
    def test_post_with_csrf_token_succeeds(self):
        """
        Test that POST with valid CSRF token succeeds.
        This verifies the CSRF protection can be satisfied.
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Get CSRF token from form
        response = self.client.get(reverse('book-create'))
        csrftoken = response.cookies['csrftoken'].value
        
        # POST with token should succeed
        response = self.client.post(
            reverse('book-create'),
            {
                'title': 'Test Book',
                'author': 'Test Author',
                'publication_year': 2024
            },
            HTTP_X_CSRFTOKEN=csrftoken
        )
        
        # Should redirect (302) or succeed (200)
        self.assertIn(response.status_code, [200, 302])
        
        # Book should be created
        self.assertTrue(Book.objects.filter(title='Test Book').exists())


class SQLInjectionTests(TestCase):
    """
    Tests to verify SQL injection prevention through Django ORM.
    
    SQL injection occurs when attackers inject malicious SQL code into
    user inputs. Django's ORM prevents this by parameterizing queries.
    """
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Add view permission
        viewer_group = Group.objects.create(name='Viewers')
        content_type = ContentType.objects.get_for_model(Book)
        permission = Permission.objects.get(
            content_type=content_type,
            codename='can_view_book'
        )
        viewer_group.permissions.add(permission)
        self.user.groups.add(viewer_group)
        
        # Create test book
        Book.objects.create(
            title='Django for Beginners',
            author='William Vincent',
            publication_year=2021
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_search_with_sql_injection_attempt_or_1_1(self):
        """
        Test that ' OR '1'='1 injection is safely handled.
        
        This is a classic SQL injection that returns all records.
        """
        response = self.client.get(reverse('book-list'), {'search': "' OR '1'='1"})
        
        # Should return 200 (no crash)
        self.assertEqual(response.status_code, 200)
    
    def test_search_with_drop_table_injection(self):
        """
        Test that DROP TABLE injection is prevented.
        """
        response = self.client.get(
            reverse('book-list'),
            {'search': "'; DROP TABLE bookshelf_book; --"}
        )
        
        # Should return 200 (not execute)
        self.assertEqual(response.status_code, 200)
        
        # Table should still exist and be queryable
        self.assertTrue(Book.objects.count() > 0)
    
    def test_search_with_valid_input_works(self):
        """
        Test that legitimate searches still work.
        """
        response = self.client.get(reverse('book-list'), {'search': 'Django'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Django for Beginners', response.content.decode())


class PermissionEnforcementTests(TestCase):
    """
    Tests to verify that permission decorators properly enforce access control.
    
    Users should only be able to access views if they have the required permission.
    """
    
    def setUp(self):
        """Set up test users with different permissions"""
        # User with no permissions
        self.no_perm_user = CustomUser.objects.create_user(
            username='noperm',
            email='noperm@example.com',
            password='testpass123'
        )
        
        # User with view permission only
        self.viewer = CustomUser.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='testpass123'
        )
        viewer_group = Group.objects.create(name='Viewers')
        content_type = ContentType.objects.get_for_model(Book)
        view_perm = Permission.objects.get(
            content_type=content_type,
            codename='can_view_book'
        )
        viewer_group.permissions.add(view_perm)
        self.viewer.groups.add(viewer_group)
        
        # User with create permission
        self.editor = CustomUser.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='testpass123'
        )
        editor_group = Group.objects.create(name='Editors')
        create_perm = Permission.objects.get(
            content_type=content_type,
            codename='can_create_book'
        )
        editor_group.permissions.add(view_perm, create_perm)
        self.editor.groups.add(editor_group)
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            publication_year=2024
        )
        
        self.client = Client()
    
    def test_unauthenticated_user_denied_access(self):
        """
        Test that unauthenticated users cannot access protected views.
        """
        response = self.client.get(reverse('book-list'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_user_without_permission_denied(self):
        """
        Test that users without required permission get 403.
        """
        self.client.login(username='noperm', password='testpass123')
        
        # Try to access view-only page
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, 403)
    
    def test_viewer_can_access_list_and_detail(self):
        """
        Test that users with view permission can access reading pages.
        """
        self.client.login(username='viewer', password='testpass123')
        
        # Should access list
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, 200)
        
        # Should access detail
        response = self.client.get(reverse('book-detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_viewer_cannot_create_book(self):
        """
        Test that viewers cannot access create page.
        """
        self.client.login(username='viewer', password='testpass123')
        
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 403)


class InputValidationTests(TestCase):
    """
    Tests to verify that inputs are properly validated and escaped.
    
    XSS (Cross-Site Scripting) attacks inject malicious scripts into content.
    Django's template auto-escaping prevents most XSS attacks.
    """
    
    def setUp(self):
        """Set up test user and client"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Add all permissions
        all_group = Group.objects.create(name='AllPerms')
        content_type = ContentType.objects.get_for_model(Book)
        all_perms = Permission.objects.filter(content_type=content_type)
        all_group.permissions.set(all_perms)
        self.user.groups.add(all_group)
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_xss_attempt_in_title_escaped(self):
        """
        Test that XSS attempts in title are escaped.
        """
        xss_payload = "<script>alert('XSS')</script>"
        
        # Try to create book with XSS payload
        response = self.client.get(reverse('book-create'))
        csrftoken = response.cookies['csrftoken'].value
        
        response = self.client.post(
            reverse('book-create'),
            {
                'title': xss_payload,
                'author': 'Test Author',
                'publication_year': 2024
            },
            HTTP_X_CSRFTOKEN=csrftoken
        )
        
        # Book should be created (form accepts it)
        self.assertTrue(Book.objects.filter(title=xss_payload).exists())
        
        # When displayed, script should be escaped
        response = self.client.get(reverse('book-list'))
        content = response.content.decode()
        
        # Should contain escaped version, not executable script
        self.assertIn('&lt;script&gt;', content)
        self.assertNotIn('<script>', content)


class SecurityHeadersTests(TestCase):
    """
    Tests to verify that security headers are properly set.
    
    Security headers tell browsers how to handle content and protect users.
    """
    
    def setUp(self):
        """Set up test user and client"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        viewer_group = Group.objects.create(name='Viewers')
        content_type = ContentType.objects.get_for_model(Book)
        permission = Permission.objects.get(
            content_type=content_type,
            codename='can_view_book'
        )
        viewer_group.permissions.add(permission)
        self.user.groups.add(viewer_group)
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_x_frame_options_header_present(self):
        """
        Test that X-Frame-Options header is set to prevent clickjacking.
        """
        response = self.client.get(reverse('book-list'))
        
        # Check for X-Frame-Options header
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
    
    def test_x_content_type_options_header_present(self):
        """
        Test that X-Content-Type-Options header prevents MIME sniffing.
        """
        response = self.client.get(reverse('book-list'))
        
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

