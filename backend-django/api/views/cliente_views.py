from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, JsonResponse

from api.models import Cliente
from api.validacao import ler_json, texto


def cliente_to_dict(cliente):
    return {
        'id': cliente.id,
        'nome': cliente.nome,
        'cpf': cliente.cpf,
        'telefone': cliente.telefone,
        'email': cliente.email,
    }


def _dados_cliente(request):
    dados = ler_json(request)
    return {
        'nome': texto(dados, 'nome', 100),
        'cpf': texto(dados, 'cpf', 14),
        'telefone': texto(dados, 'telefone', 20, obrigatorio=False),
        'email': texto(dados, 'email', 100, obrigatorio=False),
    }


def lista_clientes(request):
    if request.method == 'GET':
        return JsonResponse(
            [cliente_to_dict(c) for c in Cliente.objects.order_by('nome', 'id')],
            safe=False,
        )
    if request.method != 'POST':
        response = JsonResponse({'error': 'Método não permitido'}, status=405)
        response['Allow'] = 'GET, POST, OPTIONS'
        return response
    try:
        dados = _dados_cliente(request)
    except ValueError as erro:
        return JsonResponse({'error': str(erro)}, status=400)
    try:
        with transaction.atomic():
            cliente = Cliente.objects.create(**dados)
    except IntegrityError:
        return JsonResponse({'error': 'CPF já cadastrado'}, status=409)
    return JsonResponse(cliente_to_dict(cliente), status=201)


def detalhe_cliente(request, id):
    if request.method not in ('GET', 'PUT', 'DELETE'):
        response = JsonResponse({'error': 'Método não permitido'}, status=405)
        response['Allow'] = 'GET, PUT, DELETE, OPTIONS'
        return response
    try:
        cliente = Cliente.objects.get(pk=id)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente não encontrado'}, status=404)
    if request.method == 'GET':
        return JsonResponse(cliente_to_dict(cliente))
    if request.method == 'DELETE':
        try:
            cliente.delete()
        except ProtectedError:
            return JsonResponse(
                {'error': 'Cliente possui veículos com permanências registradas'}, status=409
            )
        return HttpResponse(status=204)
    try:
        dados = _dados_cliente(request)
    except ValueError as erro:
        return JsonResponse({'error': str(erro)}, status=400)
    for campo, valor in dados.items():
        setattr(cliente, campo, valor)
    try:
        with transaction.atomic():
            cliente.save(update_fields=list(dados))
    except IntegrityError:
        return JsonResponse({'error': 'CPF já cadastrado'}, status=409)
    return JsonResponse(cliente_to_dict(cliente))
