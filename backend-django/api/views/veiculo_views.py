import json

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, JsonResponse

from api.models import Cliente, Veiculo


CAMPOS_OBRIGATORIOS = ('placa', 'marca', 'modelo', 'cor', 'clienteId')


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


def _erro_metodo(permitidos):
    response = JsonResponse({'error': 'Método não permitido'}, status=405)
    response['Allow'] = ', '.join(permitidos + ['OPTIONS'])
    return response


def _ler_dados(request):
    try:
        dados = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return None, JsonResponse({'error': 'JSON inválido'}, status=400)

    if not isinstance(dados, dict):
        return None, JsonResponse(
            {'error': 'O corpo deve ser um objeto JSON'}, status=400
        )

    faltantes = [
        campo for campo in CAMPOS_OBRIGATORIOS
        if campo not in dados or dados[campo] is None or
        (isinstance(dados[campo], str) and not dados[campo].strip())
    ]
    if faltantes:
        return None, JsonResponse({
            'error': 'Campos obrigatórios: ' + ', '.join(faltantes)
        }, status=400)

    for campo, limite in (('placa', 10), ('marca', 50), ('modelo', 50), ('cor', 30)):
        if not isinstance(dados[campo], str):
            return None, JsonResponse(
                {'error': f"Campo '{campo}' deve ser um texto"}, status=400
            )
        dados[campo] = dados[campo].strip()
        if len(dados[campo]) > limite:
            return None, JsonResponse(
                {'error': f"Campo '{campo}' deve ter no máximo {limite} caracteres"},
                status=400,
            )

    cliente_id = dados['clienteId']
    if type(cliente_id) is not int or cliente_id <= 0:
        return None, JsonResponse(
            {'error': "Campo 'clienteId' deve ser um ID inteiro positivo"},
            status=400,
        )

    dados['placa'] = dados['placa'].upper()
    return dados, None


def lista_veiculos(request):
    if request.method != 'GET':
        return _erro_metodo(['GET'])
    veiculos = Veiculo.objects.select_related('cliente').order_by('id')
    return JsonResponse(
        [veiculo_to_dict(veiculo) for veiculo in veiculos], safe=False
    )


def criar_veiculo(request):
    if request.method != 'POST':
        return _erro_metodo(['POST'])
    dados, erro = _ler_dados(request)
    if erro:
        return erro
    if not Cliente.objects.filter(pk=dados['clienteId']).exists():
        return JsonResponse({'error': 'Cliente não encontrado.'}, status=404)
    if Veiculo.objects.filter(placa__iexact=dados['placa']).exists():
        return JsonResponse({'error': 'Já existe um veículo com esta placa.'}, status=409)
    try:
        with transaction.atomic():
            veiculo = Veiculo.objects.create(
                placa=dados['placa'],
                marca=dados['marca'],
                modelo=dados['modelo'],
                cor=dados['cor'],
                cliente_id=dados['clienteId'],
            )
    except IntegrityError:
        return JsonResponse(
            {'error': 'Já existe um veículo com esta placa.'}, status=409
        )
    veiculo = Veiculo.objects.select_related('cliente').get(pk=veiculo.pk)
    return JsonResponse(veiculo_to_dict(veiculo), status=201)


def atualizar_veiculo(request, id):
    if request.method != 'PUT':
        return _erro_metodo(['PUT'])
    try:
        veiculo = Veiculo.objects.select_related('cliente').get(pk=id)
    except Veiculo.DoesNotExist:
        return JsonResponse({'error': 'Veículo não encontrado.'}, status=404)
    dados, erro = _ler_dados(request)
    if erro:
        return erro
    if not Cliente.objects.filter(pk=dados['clienteId']).exists():
        return JsonResponse({'error': 'Cliente não encontrado.'}, status=404)
    duplicada = Veiculo.objects.filter(
        placa__iexact=dados['placa']
    ).exclude(pk=id).exists()
    if duplicada:
        return JsonResponse({'error': 'Já existe um veículo com esta placa.'}, status=409)
    veiculo.placa = dados['placa']
    veiculo.marca = dados['marca']
    veiculo.modelo = dados['modelo']
    veiculo.cor = dados['cor']
    veiculo.cliente_id = dados['clienteId']
    try:
        with transaction.atomic():
            veiculo.save(update_fields=['placa', 'marca', 'modelo', 'cor', 'cliente'])
    except IntegrityError:
        return JsonResponse(
            {'error': 'Já existe um veículo com esta placa.'}, status=409
        )
    veiculo = Veiculo.objects.select_related('cliente').get(pk=veiculo.pk)
    return JsonResponse(veiculo_to_dict(veiculo))


def excluir_veiculo(request, id):
    if request.method != 'DELETE':
        return _erro_metodo(['DELETE'])
    try:
        veiculo = Veiculo.objects.get(pk=id)
    except Veiculo.DoesNotExist:
        return JsonResponse({'error': 'Veículo não encontrado.'}, status=404)
    try:
        veiculo.delete()
    except ProtectedError:
        return JsonResponse(
            {'error': 'Não é possível excluir um veículo com permanências registradas.'},
            status=409,
        )
    return HttpResponse(status=204)


def detalhe_veiculo(request, id):
    if request.method == 'PUT':
        return atualizar_veiculo(request, id)
    if request.method == 'DELETE':
        return excluir_veiculo(request, id)
    return _erro_metodo(['PUT', 'DELETE'])


def colecao_veiculos(request):
    if request.method == 'GET':
        return lista_veiculos(request)
    if request.method == 'POST':
        return criar_veiculo(request)
    return _erro_metodo(['GET', 'POST'])
