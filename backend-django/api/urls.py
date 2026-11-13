from django.urls import path

from api.views import cliente_views, dashboard_views, vaga_views, veiculo_views


urlpatterns = [
    path('clientes/', cliente_views.lista_clientes, name='lista_clientes'),
    path('clientes/<int:id>/', cliente_views.detalhe_cliente, name='detalhe_cliente'),
    path('veiculos/', veiculo_views.lista_veiculos, name='lista_veiculos'),
    path('veiculos/<int:id>/', veiculo_views.detalhe_veiculo, name='detalhe_veiculo'),
    path('vagas/', vaga_views.lista_vagas, name='lista_vagas'),
    path('vagas/<int:id>/', vaga_views.detalhe_vaga, name='detalhe_vaga'),
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    # O frontend legado envia URLs sem barra final, inclusive em POST e PUT.
    path('clientes', cliente_views.lista_clientes),
    path('clientes/<int:id>', cliente_views.detalhe_cliente),
    path('veiculos', veiculo_views.lista_veiculos),
    path('veiculos/<int:id>', veiculo_views.detalhe_veiculo),
    path('vagas', vaga_views.lista_vagas),
    path('vagas/<int:id>', vaga_views.detalhe_vaga),
    path('dashboard', dashboard_views.dashboard),
]
