from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from api.models import Vaga
from api.serializers import serialize_vaga
from api.utils import (
    error_response, json_response, message_response, parse_json_body, require_methods,
)
from api.views.validacoes_cadastro import validar_textos

TIPOS = ('CARRO', 'MOTO')
STATUS = ('LIVRE', 'OCUPADA')


@require_methods('GET', 'POST')
def lista_vagas(request):
    if request.method == 'POST':
        return _salvar_vaga(request)

    vagas = Vaga.objects.order_by('numero', 'id')
    status = request.GET.get('status', '').strip().upper()
    if status:
        vagas = vagas.filter(status=status)
    return json_response([serialize_vaga(vaga) for vaga in vagas])


@require_methods('GET', 'PUT', 'DELETE')
def detalhe_vaga(request, id):
    try:
        vaga = Vaga.objects.get(pk=id)
    except Vaga.DoesNotExist:
        return error_response('Vaga não encontrada', status=404)

    if request.method == 'GET':
        return json_response(serialize_vaga(vaga))
    if request.method == 'PUT':
        return _salvar_vaga(request, vaga)

    try:
        with transaction.atomic():
            vaga.delete()
    except ProtectedError:
        return error_response('Não é possível excluir vaga com permanências registradas', status=409)
    return message_response('Vaga excluída com sucesso')


def _salvar_vaga(request, vaga=None):
    try:
        data = parse_json_body(request)
        dados = validar_textos(data, Vaga, ('numero',))
    except ValueError as exc:
        return error_response(exc)

    tipo = data.get('tipo')
    if tipo not in TIPOS:
        return error_response("Campo 'tipo' deve ser CARRO ou MOTO")

    novo = vaga is None
    vaga = vaga if vaga is not None else Vaga()
    if Vaga.objects.filter(numero=dados['numero']).exclude(pk=vaga.pk).exists():
        return error_response('Número de vaga já cadastrado', status=409)

    vaga.numero = dados['numero']
    vaga.tipo = tipo
    # Como no backend Java: toda vaga nasce LIVRE e status inválido no PUT vira LIVRE.
    status = data.get('status')
    vaga.status = status if not novo and status in STATUS else 'LIVRE'
    try:
        with transaction.atomic():
            vaga.save()
    except IntegrityError:
        if Vaga.objects.filter(numero=dados['numero']).exclude(pk=vaga.pk).exists():
            return error_response('Número de vaga já cadastrado', status=409)
        raise
    return json_response(serialize_vaga(vaga), status=201 if novo else 200)
