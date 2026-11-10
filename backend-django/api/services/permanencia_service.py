import math
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from api.models import Permanencia, Vaga, Veiculo


TARIFA_POR_HORA = Decimal('5.00')


class RecursoNaoEncontrado(ValueError):
    pass


@transaction.atomic
def registrar_entrada(veiculo_id, vaga_id):
    if Permanencia.objects.filter(
        veiculo_id=veiculo_id, status=Permanencia.Status.ABERTO
    ).exists():
        raise ValueError('Veículo já possui uma permanência em aberto.')

    try:
        veiculo = Veiculo.objects.get(pk=veiculo_id)
    except Veiculo.DoesNotExist:
        raise RecursoNaoEncontrado('Veículo não encontrado.') from None

    try:
        vaga = Vaga.objects.get(pk=vaga_id)
    except Vaga.DoesNotExist:
        raise RecursoNaoEncontrado('Vaga não encontrada.') from None

    if vaga.status != Vaga.Status.LIVRE:
        raise ValueError('Vaga já está ocupada.')

    vaga.status = Vaga.Status.OCUPADA
    vaga.save(update_fields=['status'])
    return Permanencia.objects.create(veiculo=veiculo, vaga=vaga)


def _calcular_valor(entrada, saida):
    duracao = saida - entrada
    horas = max(1, math.ceil(duracao / timedelta(hours=1)))
    return TARIFA_POR_HORA * horas


@transaction.atomic
def registrar_saida(permanencia_id):
    try:
        permanencia = Permanencia.objects.select_related('veiculo', 'vaga').get(pk=permanencia_id)
    except Permanencia.DoesNotExist:
        raise RecursoNaoEncontrado('Permanência não encontrada.') from None

    if permanencia.status != Permanencia.Status.ABERTO:
        raise ValueError('Permanência já foi finalizada.')

    saida = timezone.now()
    permanencia.data_hora_saida = saida
    permanencia.valor_total = _calcular_valor(permanencia.data_hora_entrada, saida)
    permanencia.status = Permanencia.Status.FINALIZADO
    permanencia.save(update_fields=['data_hora_saida', 'valor_total', 'status'])

    vaga = permanencia.vaga
    vaga.status = Vaga.Status.LIVRE
    vaga.save(update_fields=['status'])
    return permanencia
