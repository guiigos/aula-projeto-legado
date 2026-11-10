from django.urls import path

from .views import status
from .views.permanencia_views import entrada

urlpatterns = [
    path('status', status),
    path('status/', status),
    path('permanencias/entrada', entrada),
    path('permanencias/entrada/', entrada),
]
