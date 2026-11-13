import math
from datetime import datetime
from decimal import Decimal

from django.db import transaction

from api.models import Permanencia, Vaga, Veiculo

TARIFA_POR_HORA = Decimal('5.00')


class RecursoNaoEncontrado(ValueError):
    """Recurso inexistente (HTTP 404); os demais ValueError são conflitos (HTTP 409)."""


@transaction.atomic
def registrar_entrada(veiculo_id, vaga_id):
    try:
        veiculo = Veiculo.objects.get(pk=veiculo_id)
    except Veiculo.DoesNotExist:
        raise RecursoNaoEncontrado('Veículo não encontrado')

    if Permanencia.objects.filter(veiculo=veiculo, status='ABERTO').exists():
        raise ValueError('Veículo já possui uma permanência em aberto')

    try:
        vaga = Vaga.objects.select_for_update().get(pk=vaga_id)
    except Vaga.DoesNotExist:
        raise RecursoNaoEncontrado('Vaga não encontrada')

    if vaga.status != 'LIVRE':
        raise ValueError('Vaga já está ocupada')

    vaga.status = 'OCUPADA'
    vaga.save(update_fields=['status'])

    return Permanencia.objects.create(
        veiculo=veiculo,
        vaga=vaga,
        data_hora_entrada=datetime.now(),
        status='ABERTO',
    )


@transaction.atomic
def registrar_saida(permanencia_id):
    try:
        permanencia = (
            Permanencia.objects.select_for_update()
            .select_related('veiculo', 'vaga')
            .get(pk=permanencia_id)
        )
    except Permanencia.DoesNotExist:
        raise RecursoNaoEncontrado('Permanência não encontrada')

    if permanencia.status != 'ABERTO':
        raise ValueError('Permanência já foi finalizada')

    saida = datetime.now()
    permanencia.data_hora_saida = saida
    permanencia.valor_total = calcular_valor(permanencia.data_hora_entrada, saida)
    permanencia.status = 'FINALIZADO'
    permanencia.save()

    vaga = permanencia.vaga
    vaga.status = 'LIVRE'
    vaga.save(update_fields=['status'])

    return permanencia


def calcular_valor(entrada, saida):
    """Cobra R$ 5,00 por hora iniciada, com mínimo de 1 hora (regra do backend Java)."""
    # Minutos completos, como o ChronoUnit.MINUTES.between do Java.
    minutos = int((saida - entrada).total_seconds() // 60)
    horas = max(math.ceil(minutos / 60), 1)
    return TARIFA_POR_HORA * horas
