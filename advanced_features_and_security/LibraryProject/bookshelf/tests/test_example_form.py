from django.test import TestCase
from django.urls import reverse
from .forms import ExampleForm


class ExampleFormTests(TestCase):
    def test_example_form_fields(self):
        form = ExampleForm()
        self.assertIn('name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('message', form.fields)
        self.assertIn('subscribe', form.fields)

    def test_example_form_validation(self):
        data = {'name': 'Alice', 'email': 'alice@example.com'}
        form = ExampleForm(data)
        self.assertTrue(form.is_valid())


class ExampleViewTests(TestCase):
    def test_get_example_view(self):
        resp = self.client.get(reverse('example'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

    def test_post_example_view_redirect(self):
        resp = self.client.post(reverse('example'), {'name': 'Bob', 'email': 'bob@example.com'})
        self.assertEqual(resp.status_code, 302)  # redirected after successful POST