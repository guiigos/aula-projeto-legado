from django.urls import path

from .views import status
from .views.cliente_views import lista_clientes, detalhe_cliente
from .views.vaga_views import lista_vagas, detalhe_vaga
from .views.dashboard_views import dashboard
from .views.permanencia_views import entrada, lista_permanencias, saida
from .views.veiculo_views import (
    colecao_veiculos,
    detalhe_veiculo,
)

urlpatterns = [
    path('clientes', lista_clientes),
    path('clientes/', lista_clientes),
    path('clientes/<int:id>', detalhe_cliente),
    path('clientes/<int:id>/', detalhe_cliente),
    path('vagas', lista_vagas),
    path('vagas/', lista_vagas),
    path('vagas/<int:id>', detalhe_vaga),
    path('vagas/<int:id>/', detalhe_vaga),
    path('dashboard', dashboard),
    path('dashboard/', dashboard),
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
