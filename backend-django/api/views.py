from django.http import JsonResponse, HttpResponseBadRequest

from .dashboard import DashboardEndPoints
from .cliente import ClientEndPoints
from .veiculo import VeiculoEndPoints
from .vaga import VagaEndPoints 
from .permanencia import PermanenciaEndPoints

def handle_dashboard(request):
    if request.method == 'GET':
        return DashboardEndPoints.get_dashboard_data(request)

    return JsonResponse(
            {'erro': 'Metodo nao permitido'},
            status=405
        )

def handle_cliente(request):
    if request.method == 'GET':
        return ClientEndPoints.get_clientes()

    if request.method == 'POST':
        return ClientEndPoints.post_clientes(request)

    return JsonResponse(
            {'erro': 'Metodo nao permitido'},
            status=405
        )

def handle_cliente_by_id(request, id=None):
    if id is None:
        return HttpResponseBadRequest()

    if request.method == 'GET':
        return ClientEndPoints.get_cliente_by_id(id)
    if request.method == 'PUT':
        return ClientEndPoints.put_cliente_by_id(request, id)
    if request.method == 'DELETE':
        return ClientEndPoints.delete_cliente_by_id(id)

    return JsonResponse(
            {'erro': 'Metodo nao permitido'},
            status=405
        )

def handle_veiculo(request):
    if request.method == 'GET':
        return VeiculoEndPoints.get_veiculos(request)

    if request.method == 'POST':
        return VeiculoEndPoints.post_veiculos(request)

    return JsonResponse(
        {'erro': 'Método não permitido'},
        status=405
    )

def handle_veiculo_by_id(request, id):
    if request.method == 'GET':
        return VeiculoEndPoints.get_veiculo_by_id(request, id)

    if request.method == 'PUT':
        return VeiculoEndPoints.put_veiculo_by_id(request, id)

    if request.method == 'DELETE':
        return VeiculoEndPoints.delete_veiculo_by_id(request, id)

    return JsonResponse(
        {'erro': 'Método não permitido'},
        status=405
    )

def handle_permanencia(request):
    if request.method == 'GET':
        return PermanenciaEndPoints.get_permanencias(request)

    if request.method == 'POST':
        return PermanenciaEndPoints.post_permanencias(request)

    return JsonResponse(
        {'erro': 'Método não permitido'},
        status=405
    )

def handle_permanencia_by_id(request, id):
    if request.method == 'PUT':
        return PermanenciaEndPoints.put_permanencia_by_id(request, id)

    return JsonResponse(
        {'erro': 'Método não permitido'},
        status=405
    )

def handle_vaga(request):
    if request.method == 'GET':
        return VagaEndPoints.get_vagas(request)

    if request.method == 'POST':
        return VagaEndPoints.post_vagas(request)

    return JsonResponse(
        {'error': 'Método não permitido'},
        status=405
    )

def handle_vaga_by_id(request, id):
    if request.method == 'GET':
        return VagaEndPoints.get_vaga_by_id(request, id)

    if request.method == 'PUT':
        return VagaEndPoints.put_vaga_by_id(request, id)

    if request.method == 'DELETE':
        return VagaEndPoints.delete_vaga_by_id(request, id)

    return JsonResponse(
        {'error': 'Método não permitido'},
        status=405
    )


