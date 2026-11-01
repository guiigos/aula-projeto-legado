import json

from django.db import IntegrityError
from ..models import Veiculo
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from ..models import Veiculo, Cliente

def get_veiculos():
    veiculos = Veiculo.objects.all()

    dados = [
        veiculo_to_dict(veiculo)
        for veiculo in veiculos
    ]

    return JsonResponse(dados, safe=False, status=200)

def post_veiculos(request):
    body = json.loads(request.body)

    resultado = validar(body)
    if resultado is not None:
        return resultado

    veiculo = Veiculo(
        placa = body.get("placa"),
        marca = body.get("marca"),
        modelo = body.get("modelo"),
        cor = body.get("cor"),
    )

    cliente_id = body.get('clienteId')
    veiculo.cliente = get_object_or_404(Cliente, id=cliente_id)

    try:
        veiculo.save()
        return JsonResponse(veiculo_to_dict(veiculo), status=201)
    except IntegrityError:
        return JsonResponse({
            "error": "Placa já cadastrada"
        }, status=409)

def get_veiculo_by_id(id):
    veiculo = get_object_or_404(Veiculo, id=id)

    return JsonResponse(veiculo_to_dict(veiculo), status=200)

def delete_veiculo_by_id(id):
    veiculo = get_object_or_404(Veiculo, id=id)
    veiculo.delete()
    return HttpResponse(status=204)

def put_veiculo_by_id(request, id):
    veiculo = get_object_or_404(Veiculo, id=id)
    body = json.loads(request.body)

    resultado = validar(body)
    if resultado is not None:
        return resultado

    for value in ('placa', 'marca', 'modelo', 'cor'):
        setattr(veiculo, value, body.get(value))

    veiculo.save()
    return JsonResponse(veiculo_to_dict(veiculo), status=200)

def validar(body):
    if not body.get('placa'):
        return JsonResponse({"mensagem": "Campo 'placa' é obrigatório"}, status=400)
    if not body.get('marca'):
        return JsonResponse({"mensagem": "Campo 'marca' é obrigatório"}, status=400)
    if not body.get('modelo'):
        return JsonResponse({"mensagem": "Campo 'modelo' é obrigatório"}, status=400)
    if not body.get('cor'):
        return JsonResponse({"mensagem": "Campo 'cor' é obrigatório"}, status=400)
    if not body.get('clienteId'):
        return JsonResponse({"mensagem": "Campo 'clienteId' é obrigatório"}, status=400)
    
    return None
        
def veiculo_to_dict(veiculo):
    return {
        'id': veiculo.id,
        'placa': veiculo.placa,
        'marca': veiculo.marca,
        'modelo': veiculo.modelo,
        'cor': veiculo.cor,
        'clienteId': veiculo.cliente_id,
        'clienteNome': veiculo.cliente.nome,
    }
