import json


from django.utils import timezone
from django.db import transaction

from ..models import Veiculo
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from ..models import Veiculo, Cliente, Permanencia, Vaga

from decimal import Decimal


TARIFA_POR_HORA = Decimal('5.00')


def calcular_valor(entrada, saida):
    minutos = int((saida - entrada).total_seconds() // 60)
    horas = max(1, (minutos + 59) // 60)
    return TARIFA_POR_HORA * horas

def get_permanencias(request):
    permanencias = Permanencia.objects.select_related('veiculo', 'vaga').all().order_by('-data_hora_entrada')

    status = request.GET.get('status')
    if status:
        permanencias = permanencias.filter(status=status)

    dados = [
        permanencia_to_dict(permanencia)
        for permanencia in permanencias
    ]

    return JsonResponse(dados, safe=False, status=200)

def post_permanencias(request):
    data = json.loads(request.body)

    veiculo_id = data.get('veiculoId')
    vaga_id = data.get('vagaId')

    # Java: 400 se faltar campo
    if not veiculo_id or not vaga_id:
        return JsonResponse({'error': "Campos 'veiculoId' e 'vagaId' são obrigatórios"}, status=400)

    with transaction.atomic():
        # Java: existsVeiculoAberto -> 409
        if Permanencia.objects.filter(veiculo_id=veiculo_id, status=Permanencia.Status.ABERTO).exists():
            return JsonResponse({'error': 'Veículo já possui uma permanência em aberto.'}, status=409)

        veiculo = Veiculo.objects.filter(id=veiculo_id).first()
        if veiculo is None:
            return JsonResponse({'error': 'Veículo não encontrado.'}, status=404)

        # Java: findByIdForUpdate -> 404
        vaga = Vaga.objects.select_for_update().filter(id=vaga_id).first()
        if vaga is None:
            return JsonResponse({'error': 'Vaga não encontrada.'}, status=404)

        # Java: vaga OCUPADA -> 409
        if vaga.status == Vaga.Status.OCUPADA:
            return JsonResponse({'error': 'Vaga já está ocupada.'}, status=409)

        # Java: updateStatus(vagaId, "OCUPADA")
        vaga.status = Vaga.Status.OCUPADA
        vaga.save()

        # Java: permanenciaRepository.save(p)
        permanencia = Permanencia.objects.create(
            veiculo=veiculo,
            vaga=vaga,
            data_hora_entrada=timezone.now(),
            status=Permanencia.Status.ABERTO,
        )

    return JsonResponse(permanencia_to_dict(permanencia), status=201)

def put_permanencia_by_id(request, id):
    with transaction.atomic():
        permanencia = Permanencia.objects.select_for_update().select_related('veiculo', 'vaga').filter(id=id).first()
        if permanencia is None:
            return JsonResponse({'error': 'Permanência não encontrada.'}, status=404)

        if permanencia.status == Permanencia.Status.FINALIZADO:
            return JsonResponse({'error': 'Permanência já foi finalizada.'}, status=409)

        saida = timezone.now()
        permanencia.data_hora_saida = saida
        permanencia.valor_total = calcular_valor(permanencia.data_hora_entrada, saida)
        permanencia.status = Permanencia.Status.FINALIZADO
        permanencia.save()

        vaga = permanencia.vaga
        vaga.status = Vaga.Status.LIVRE
        vaga.save()

    return JsonResponse(permanencia_to_dict(permanencia), status=200)

def permanencia_to_dict(permanencia):
    return {
        'id': permanencia.id,
        'veiculoId': permanencia.veiculo.id,
        'vagaId': permanencia.vaga.id,
        'dataHoraEntrada': permanencia.data_hora_entrada.isoformat(),
        'dataHoraSaida': permanencia.data_hora_saida.isoformat() if permanencia.data_hora_saida else None,
        'valorTotal': str(permanencia.valor_total) if permanencia.valor_total is not None else None,
        'veiculoPlaca': permanencia.veiculo.placa,
        'veiculoModelo': permanencia.veiculo.modelo,
        'vagaNumero': permanencia.vaga.numero,
        'status': permanencia.status
    }

