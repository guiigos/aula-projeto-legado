import json
from django.db import IntegrityError

from django.http import JsonResponse
from ..models import Vaga

from django.http import JsonResponse, HttpResponse
from django.db.models.deletion import ProtectedError

def vaga_to_dict(vaga):
    return {
        'id': vaga.id,
        'numero': vaga.numero,
        'tipo': vaga.tipo,
        'status': vaga.status,
    }

def get_vagas(request):
    vagas = Vaga.objects.all().order_by('numero')

    status = request.GET.get('status')

    if status:
        if status not in ('LIVRE', 'OCUPADA'):
            return JsonResponse(
                {'error': 'Status inválido'},
                status=400
            )

        vagas = vagas.filter(status=status)

    dados = [
        vaga_to_dict(vaga)
        for vaga in vagas
    ]

    return JsonResponse(dados, safe=False, status=200)

def get_vaga_by_id(request, id):
    try:
        vaga = Vaga.objects.get(id=id)

        return JsonResponse(
            vaga_to_dict(vaga),
            status=200
        )

    except Vaga.DoesNotExist:
        return JsonResponse(
            {'error': 'Vaga não encontrada'},
            status=404
        )

    
def post_vagas(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {'error': 'JSON inválido'},
            status=400
        )

    if not isinstance(body, dict):
        return JsonResponse(
            {'error': 'Dados inválidos'},
            status=400
        )

    numero = body.get('numero')
    tipo = body.get('tipo')

    # Validar campos obrigatórios
    if not isinstance(numero, str) or not numero.strip():
        return JsonResponse(
            {'error': 'Campo numero é obrigatório'},
            status=400
        )

    if tipo not in ('CARRO', 'MOTO'):
        return JsonResponse(
            {'error': 'Tipo deve ser CARRO ou MOTO'},
            status=400
        )

    numero = numero.strip().upper()

    if len(numero) > 20:
        return JsonResponse(
            {'error': 'Número deve ter até 20 caracteres'},
            status=400
        )

    # Verificar duplicidade
    if Vaga.objects.filter(numero=numero).exists():
        return JsonResponse(
            {'error': 'Número de vaga já cadastrado'},
            status=409
        )

    try:
        vaga = Vaga.objects.create(
            numero=numero,
            tipo=tipo
        )
    except IntegrityError:
        return JsonResponse(
            {'error': 'Número de vaga já cadastrado'},
            status=409
        )

    return JsonResponse(
        vaga_to_dict(vaga),
        status=201
    )


def put_vaga_by_id(request, id):
    try:
        vaga = Vaga.objects.get(id=id)
    except Vaga.DoesNotExist:
        return JsonResponse(
            {'error': 'Vaga não encontrada'},
            status=404
        )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {'error': 'JSON inválido'},
            status=400
        )

    if not isinstance(body, dict):
        return JsonResponse(
            {'error': 'Dados inválidos'},
            status=400
        )

    numero = body.get('numero')
    tipo = body.get('tipo')
    status = body.get('status', vaga.status)

    # Validar campos obrigatórios
    if not isinstance(numero, str) or not numero.strip():
        return JsonResponse(
            {'error': 'Campo numero é obrigatório'},
            status=400
        )

    numero = numero.strip().upper()

    if len(numero) > 20:
        return JsonResponse(
            {'error': 'Número deve ter até 20 caracteres'},
            status=400
        )

    if tipo not in ('CARRO', 'MOTO'):
        return JsonResponse(
            {'error': 'Tipo deve ser CARRO ou MOTO'},
            status=400
        )

    if status not in ('LIVRE', 'OCUPADA'):
        return JsonResponse(
            {'error': 'Status inválido'},
            status=400
        )

    # Verificar se o número já pertence a outra vaga
    if Vaga.objects.filter(numero=numero).exclude(id=id).exists():
        return JsonResponse(
            {'error': 'Número de vaga já cadastrado'},
            status=409
        )

    vaga.numero = numero
    vaga.tipo = tipo
    vaga.status = status

    try:
        vaga.save()
    except IntegrityError:
        return JsonResponse(
            {'error': 'Número de vaga já cadastrado'},
            status=409
        )

    return JsonResponse(
        vaga_to_dict(vaga),
        status=200
    )


def delete_vaga_by_id(request, id):
    try:
        vaga = Vaga.objects.get(id=id)

    except Vaga.DoesNotExist:
        return JsonResponse(
            {'error': 'Vaga não encontrada'},
            status=404
        )

    try:
        vaga.delete()

    except ProtectedError:
        return JsonResponse(
            {
                'error': 'Não é possível excluir vaga com permanências registradas'
            },
            status=409
        )

    return HttpResponse(status=204)
