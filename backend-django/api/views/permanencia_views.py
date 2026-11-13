from api.models import Permanencia
from api.serializers import serialize_permanencia
from api.services import permanencia_service
from api.services.permanencia_service import RecursoNaoEncontrado
from api.utils import error_response, json_response, parse_json_body, require_methods


def _id_valido(valor):
    """Aceita apenas inteiros positivos (booleanos e frações são rejeitados)."""
    return type(valor) is int and 0 < valor <= 9223372036854775807


@require_methods('GET')
def lista_permanencias(request):
    permanencias = (
        Permanencia.objects.select_related('veiculo', 'vaga')
        .order_by('-data_hora_entrada', '-id')
    )
    status = request.GET.get('status', '').strip().upper()
    if status:
        permanencias = permanencias.filter(status=status)
    return json_response([serialize_permanencia(p) for p in permanencias])


@require_methods('POST')
def entrada(request):
    try:
        data = parse_json_body(request)
    except ValueError as exc:
        return error_response(exc)

    veiculo_id = data.get('veiculoId')
    vaga_id = data.get('vagaId')
    if not _id_valido(veiculo_id) or not _id_valido(vaga_id):
        return error_response("Campos 'veiculoId' e 'vagaId' são obrigatórios e devem ser inteiros positivos")

    try:
        permanencia = permanencia_service.registrar_entrada(veiculo_id, vaga_id)
    except RecursoNaoEncontrado as exc:
        return error_response(exc, status=404)
    except ValueError as exc:
        return error_response(exc, status=409)
    return json_response(serialize_permanencia(permanencia), status=201)


@require_methods('PUT')
def saida(request, id):
    try:
        permanencia = permanencia_service.registrar_saida(id)
    except RecursoNaoEncontrado as exc:
        return error_response(exc, status=404)
    except ValueError as exc:
        return error_response(exc, status=409)
    return json_response(serialize_permanencia(permanencia))
