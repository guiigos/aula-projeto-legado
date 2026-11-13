from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from api.models import Cliente, Veiculo
from api.serializers import serialize_veiculo
from api.utils import (
    error_response, json_response, message_response, parse_json_body, require_methods,
)
from api.views.validacoes_cadastro import validar_cliente_id, validar_textos


@require_methods('GET', 'POST')
def lista_veiculos(request):
    if request.method == 'POST':
        return _salvar_veiculo(request)

    veiculos = Veiculo.objects.select_related('cliente').order_by('placa', 'id')
    busca = request.GET.get('busca', '').strip()
    if busca:
        veiculos = veiculos.filter(
            Q(placa__icontains=busca) | Q(marca__icontains=busca)
            | Q(modelo__icontains=busca) | Q(cor__icontains=busca)
            | Q(cliente__nome__icontains=busca)
        )
    return json_response([serialize_veiculo(veiculo) for veiculo in veiculos])


@require_methods('GET', 'PUT', 'DELETE')
def detalhe_veiculo(request, id):
    try:
        veiculo = Veiculo.objects.select_related('cliente').get(pk=id)
    except Veiculo.DoesNotExist:
        return error_response('Veículo não encontrado', status=404)

    if request.method == 'GET':
        return json_response(serialize_veiculo(veiculo))
    if request.method == 'PUT':
        return _salvar_veiculo(request, veiculo)

    try:
        with transaction.atomic():
            veiculo.delete()
    except ProtectedError:
        return error_response(
            'Não é possível excluir veículo com permanências registradas', status=409,
        )
    return message_response('Veículo excluído com sucesso')


def _salvar_veiculo(request, veiculo=None):
    try:
        data = parse_json_body(request)
        dados = validar_textos(data, Veiculo, ('placa', 'marca', 'modelo', 'cor'))
        cliente_id = validar_cliente_id(data.get('clienteId'))
    except ValueError as exc:
        return error_response(exc)

    try:
        cliente = Cliente.objects.get(pk=cliente_id)
    except Cliente.DoesNotExist:
        return error_response('Cliente não encontrado', status=404)

    novo = veiculo is None
    veiculo = veiculo if veiculo is not None else Veiculo()
    # O formulário legado também converte placas para maiúsculas.
    dados['placa'] = dados['placa'].upper()
    if Veiculo.objects.filter(placa__iexact=dados['placa']).exclude(pk=veiculo.pk).exists():
        return error_response('Placa já cadastrada', status=409)

    for campo, valor in dados.items():
        setattr(veiculo, campo, valor)
    veiculo.cliente = cliente
    try:
        with transaction.atomic():
            veiculo.save()
    except IntegrityError:
        if Veiculo.objects.filter(placa__iexact=dados['placa']).exclude(pk=veiculo.pk).exists():
            return error_response('Placa já cadastrada', status=409)
        if not Cliente.objects.filter(pk=cliente_id).exists():
            return error_response('Cliente não encontrado', status=404)
        raise
    return json_response(serialize_veiculo(veiculo), status=201 if novo else 200)
