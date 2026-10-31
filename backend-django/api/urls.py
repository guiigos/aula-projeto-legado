from django.urls import path

from .views import *

urlpatterns = [
    path('clientes', handle_cliente),
    path('clientes/<int:id>', handle_cliente_by_id),

    path('veiculos', handle_veiculo),
    path('veiculos/<int:id>', handle_veiculo_by_id),

    path('permanencias', handle_permanencia),
    path('permanencias/<int:id>/saida', handle_permanencia_by_id),
    path('permanencias/entrada', handle_permanencia)

]
    

