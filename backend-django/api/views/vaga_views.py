from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, JsonResponse

from api.models import Permanencia, Vaga
from api.validacao import ler_json, texto


def vaga_to_dict(vaga):
    return {'id': vaga.id, 'numero': vaga.numero, 'tipo': vaga.tipo, 'status': vaga.status}


def _dados_vaga(request, status_padrao=Vaga.Status.LIVRE):
    dados = ler_json(request)
    numero = texto(dados, 'numero', 10).upper()
    tipo = texto(dados, 'tipo', 5)
    status = dados.get('status', status_padrao)
    if tipo not in Vaga.Tipo.values:
        raise ValueError('Tipo deve ser CARRO ou MOTO')
    if status not in Vaga.Status.values:
        raise ValueError('Status deve ser LIVRE ou OCUPADA')
    return {'numero': numero, 'tipo': tipo, 'status': status}


def lista_vagas(request):
    if request.method == 'GET':
        vagas = Vaga.objects.order_by('numero', 'id')
        status = request.GET.get('status')
        if status:
            vagas = vagas.filter(status=status)
        return JsonResponse([vaga_to_dict(v) for v in vagas], safe=False)
    if request.method != 'POST':
        response = JsonResponse({'error': 'Método não permitido'}, status=405)
        response['Allow'] = 'GET, POST, OPTIONS'
        return response
    try:
        dados = _dados_vaga(request)
    except ValueError as erro:
        return JsonResponse({'error': str(erro)}, status=400)
    try:
        with transaction.atomic():
            vaga = Vaga.objects.create(**dados)
    except IntegrityError:
        return JsonResponse({'error': 'Número de vaga já cadastrado'}, status=409)
    return JsonResponse(vaga_to_dict(vaga), status=201)


def detalhe_vaga(request, id):
    if request.method not in ('GET', 'PUT', 'DELETE'):
        response = JsonResponse({'error': 'Método não permitido'}, status=405)
        response['Allow'] = 'GET, PUT, DELETE, OPTIONS'
        return response
    # A transação mantém a edição sincronizada com as entradas e saídas.
    with transaction.atomic():
        try:
            vaga = Vaga.objects.get(pk=id)
        except Vaga.DoesNotExist:
            return JsonResponse({'error': 'Vaga não encontrada'}, status=404)
        if request.method == 'GET':
            return JsonResponse(vaga_to_dict(vaga))
        if request.method == 'DELETE':
            try:
                vaga.delete()
            except ProtectedError:
                return JsonResponse({'error': 'Vaga possui permanências registradas'}, status=409)
            return HttpResponse(status=204)
        try:
            dados = _dados_vaga(request, vaga.status)
        except ValueError as erro:
            return JsonResponse({'error': str(erro)}, status=400)
        if dados['status'] != Vaga.Status.OCUPADA and Permanencia.objects.filter(
            vaga=vaga, status=Permanencia.Status.ABERTO
        ).exists():
            return JsonResponse(
                {'error': 'Registre a saída antes de liberar a vaga'}, status=409
            )
        for campo, valor in dados.items():
            setattr(vaga, campo, valor)
        try:
            with transaction.atomic():
                vaga.save(update_fields=list(dados))
        except IntegrityError:
            return JsonResponse({'error': 'Número de vaga já cadastrado'}, status=409)
    return JsonResponse(vaga_to_dict(vaga))
