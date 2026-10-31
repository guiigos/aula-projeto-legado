import json

from ..models import Veiculo
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from ..models import Veiculo, Cliente, Permanencia, Vaga


def get_permanencias():
    permanencias = Permanencia.objects.all()

    dados = [
        permanencia_to_dict(permanencia)
        for permanencia in permanencias
    ]

    return JsonResponse(dados, safe=False, status=200)

def post_permanencias(request):
    data = json.loads(request.body)

    cliente_id = data.get('cliente_id')
    veiculo_id = data.get('veiculo_id')
    vaga_id = data.get('vaga_id')

    cliente = get_object_or_404(Cliente, id=cliente_id)
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)
    vaga = get_object_or_404(Vaga, id=vaga_id)

    permanencia = Permanencia(cliente=cliente, veiculo=veiculo, vaga=vaga)
    permanencia.save()

    return JsonResponse(permanencia_to_dict(permanencia), status=201)

def put_permanencia_by_id(request, id):
    permanencia = get_object_or_404(Permanencia, id=id)
    data = json.loads(request.body)

    if 'saida' in data:
        permanencia.saida = data['saida']

    permanencia.save()

    return JsonResponse(permanencia_to_dict(permanencia), status=200)

def permanencia_to_dict(permanencia):
    return {
        'id': permanencia.id,
        'cliente_id': permanencia.cliente.id,
        'veiculo_id': permanencia.veiculo.id,
        'vaga_id': permanencia.vaga.id,
        'entrada': permanencia.entrada.isoformat(),
        'saida': permanencia.saida.isoformat() if permanencia.saida else None
    }

