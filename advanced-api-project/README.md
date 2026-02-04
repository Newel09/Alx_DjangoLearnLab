# advanced-api-project

This project scaffolds a Django project prepared for advanced API development with Django REST Framework.

Quick setup (local):

1. Create & activate a virtual environment:
   - python -m venv venv
   - venv\Scripts\activate  (Windows)

2. Install dependencies:
   - pip install django djangorestframework

3. Run migrations:
   - python manage.py makemigrations
   - python manage.py migrate

4. Run tests:
   - python manage.py test

Project highlights:
- `api/models.py` defines `Author` and `Book` models with a FK relationship (one Author -> many Books).
- `api/serializers.py` implements `BookSerializer` (with publication_year validation) and `AuthorSerializer` (includes nested `books`).

Next steps: add views and endpoints for the API and expand the serializers for write operations if desired.
