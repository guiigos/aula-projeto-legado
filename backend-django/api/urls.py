from django.urls import path

from api.views import (
    cliente_views, dashboard_views, permanencia_views, vaga_views, veiculo_views,
)


urlpatterns = [
    path('clientes/', cliente_views.lista_clientes, name='lista_clientes'),
    path('clientes/<int:id>/', cliente_views.detalhe_cliente, name='detalhe_cliente'),
    path('veiculos/', veiculo_views.lista_veiculos, name='lista_veiculos'),
    path('veiculos/<int:id>/', veiculo_views.detalhe_veiculo, name='detalhe_veiculo'),
    path('vagas/', vaga_views.lista_vagas, name='lista_vagas'),
    path('vagas/<int:id>/', vaga_views.detalhe_vaga, name='detalhe_vaga'),
    path('permanencias/', permanencia_views.lista_permanencias, name='lista_permanencias'),
    path('permanencias/entrada/', permanencia_views.entrada, name='entrada_permanencia'),
    path('permanencias/<int:id>/saida/', permanencia_views.saida, name='saida_permanencia'),
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    # O frontend legado envia URLs sem barra final, inclusive em POST e PUT.
    path('clientes', cliente_views.lista_clientes),
    path('clientes/<int:id>', cliente_views.detalhe_cliente),
    path('veiculos', veiculo_views.lista_veiculos),
    path('veiculos/<int:id>', veiculo_views.detalhe_veiculo),
    path('vagas', vaga_views.lista_vagas),
    path('vagas/<int:id>', vaga_views.detalhe_vaga),
    path('permanencias', permanencia_views.lista_permanencias),
    path('permanencias/entrada', permanencia_views.entrada),
    path('permanencias/<int:id>/saida', permanencia_views.saida),
    path('dashboard', dashboard_views.dashboard),
]
