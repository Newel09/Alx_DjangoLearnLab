# api_project

This is a minimal Django project scaffold prepared for building APIs with Django REST Framework.

## Setup (local)

1. Create and activate a virtual environment (recommended):
   - python -m venv venv
   - venv\Scripts\activate  (Windows)

2. Install dependencies:
   - pip install django djangorestframework

3. Run migrations and start the server:
   - python manage.py makemigrations
   - python manage.py migrate
   - python manage.py runserver

4. Visit http://127.0.0.1:8000/ (you should see "API project is running")

Next steps: add serializers and views to `api/` to build REST endpoints. Happy building! 🚀
