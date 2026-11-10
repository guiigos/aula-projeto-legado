from django.db import transaction

from api.models import Permanencia, Vaga, Veiculo


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
