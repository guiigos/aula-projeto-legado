from django.urls import path

from .views import status
from .views.permanencia_views import entrada, lista_permanencias, saida

urlpatterns = [
    path('status', status),
    path('status/', status),
    path('permanencias', lista_permanencias),
    path('permanencias/', lista_permanencias),
    path('permanencias/entrada', entrada),
    path('permanencias/entrada/', entrada),
    path('permanencias/<int:id>/saida', saida),
    path('permanencias/<int:id>/saida/', saida),
]
