from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def root(request):
    return HttpResponse('API project is running')

urlpatterns = [
    path('', root),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
