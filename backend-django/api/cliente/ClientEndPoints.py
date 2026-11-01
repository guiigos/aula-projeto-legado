import json

from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from ..models import Cliente
from django.http import JsonResponse, HttpResponse

def get_clientes():
    clientes = Cliente.objects.all()

    dados = [
        cliente_to_dict(cliente)
        for cliente in clientes
    ]

    return JsonResponse(dados, safe=False, status=200)

def post_clientes(request):
    body = json.loads(request.body)

    if not body.get('nome'):
        return JsonResponse({"mensagem": "Campo 'nome' é obrigatório"}, status=400)
    if not body.get('cpf'):
        return JsonResponse({"mensagem": "Campo 'cpf' é obrigatório"}, status=400)


    cliente = Cliente(
        nome=body.get('nome'),
        cpf=body.get('cpf'),
        telefone=body.get('telefone'),
        email=body.get('email'),
    )

    try:
        cliente.save()
        return JsonResponse(cliente_to_dict(cliente), status=201)
    
    except IntegrityError:
        return JsonResponse({
            "error": "CPF já cadastrado"
        }, status=409)


def get_cliente_by_id(id):
    cliente = get_object_or_404(Cliente, id=id)

    return JsonResponse(cliente_to_dict(cliente), safe=False, status=200)

def put_cliente_by_id(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    body = json.loads(request.body)

    if not body.get('nome'):
        return JsonResponse({"mensagem": "Campo 'nome' é obrigatório"}, status=400)
    if not body.get('cpf'):
        return JsonResponse({"mensagem": "Campo 'cpf' é obrigatório"}, status=400)

    for value in ('nome', 'cpf', 'telefone', 'email'):
        if value in body:
            setattr(cliente, value, body.get(value))

    try:
        cliente.save()
        return JsonResponse(cliente_to_dict(cliente), status=200)

    except IntegrityError:
        return JsonResponse({
            "error": "CPF já cadastrado"
        }, status=500)

def delete_cliente_by_id(id):
    cliente = get_object_or_404(Cliente, id=id)

    try:
        cliente.delete()
        return HttpResponse(status=204)
    
    except IntegrityError:
        return JsonResponse({
            "mensagem": "Não é possível excluir cliente com veículos cadastrados"
            }, status=409)

def cliente_to_dict(cliente):
    return {
        'id': cliente.id,
        'nome': cliente.nome,
        'cpf': cliente.cpf,
        'telefone': cliente.telefone,
        'email': cliente.email,
    }