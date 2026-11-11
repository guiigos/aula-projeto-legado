from django.urls import path

from .views import status
from .views.permanencia_views import entrada, lista_permanencias, saida
from .views.veiculo_views import (
    colecao_veiculos,
    detalhe_veiculo,
)

urlpatterns = [
    path('status', status),
    path('status/', status),
    path('permanencias', lista_permanencias),
    path('permanencias/', lista_permanencias),
    path('permanencias/entrada', entrada),
    path('permanencias/entrada/', entrada),
    path('permanencias/<int:id>/saida', saida),
    path('permanencias/<int:id>/saida/', saida),
    path('veiculos', colecao_veiculos),
    path('veiculos/', colecao_veiculos),
    path('veiculos/<int:id>', detalhe_veiculo),
    path('veiculos/<int:id>/', detalhe_veiculo),
]
