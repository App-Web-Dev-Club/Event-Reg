from django.urls import path
from .views import FormCreate

urlpatterns = [
    path('create_form/', FormCreate.as_view(), name='create_form'),
    path('list_forms/', FormCreate.as_view(), name='list_forms'),
    # Add more URL patterns as needed
]