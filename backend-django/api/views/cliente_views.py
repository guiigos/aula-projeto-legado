from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from api.models import Cliente
from api.serializers import serialize_cliente
from api.utils import (
    error_response, json_response, message_response, parse_json_body, require_methods,
)
from api.views.validacoes_cadastro import validar_textos


@require_methods('GET', 'POST')
def lista_clientes(request):
    if request.method == 'POST':
        return _salvar_cliente(request)

    clientes = Cliente.objects.order_by('nome', 'id')
    busca = request.GET.get('busca', '').strip()
    if busca:
        clientes = clientes.filter(Q(nome__icontains=busca) | Q(cpf__icontains=busca))
    return json_response([serialize_cliente(cliente) for cliente in clientes])


@require_methods('GET', 'PUT', 'DELETE')
def detalhe_cliente(request, id):
    try:
        cliente = Cliente.objects.get(pk=id)
    except Cliente.DoesNotExist:
        return error_response('Cliente não encontrado', status=404)

    if request.method == 'GET':
        return json_response(serialize_cliente(cliente))
    if request.method == 'PUT':
        return _salvar_cliente(request, cliente)

    try:
        with transaction.atomic():
            cliente.delete()
    except ProtectedError:
        return error_response(
            'Não é possível excluir cliente com veículos que possuem permanências registradas',
            status=409,
        )
    return message_response('Cliente excluído com sucesso')


def _salvar_cliente(request, cliente=None):
    try:
        data = parse_json_body(request)
        dados = validar_textos(data, Cliente, ('nome', 'cpf'), ('telefone', 'email'))
    except ValueError as exc:
        return error_response(exc)

    novo = cliente is None
    cliente = cliente if cliente is not None else Cliente()
    duplicados = Cliente.objects.filter(cpf=dados['cpf']).exclude(pk=cliente.pk)
    if duplicados.exists():
        return error_response('CPF já cadastrado', status=409)

    for campo, valor in dados.items():
        setattr(cliente, campo, valor)
    try:
        with transaction.atomic():
            cliente.save()
    except IntegrityError:
        if Cliente.objects.filter(cpf=dados['cpf']).exclude(pk=cliente.pk).exists():
            return error_response('CPF já cadastrado', status=409)
        raise
    return json_response(serialize_cliente(cliente), status=201 if novo else 200)
