import json

from django.http import JsonResponse

from api.services.permanencia_service import RecursoNaoEncontrado, registrar_entrada


def permanencia_to_dict(permanencia):
    saida = permanencia.data_hora_saida
    valor = permanencia.valor_total
    return {
        'id': permanencia.id,
        'veiculoId': permanencia.veiculo_id,
        'veiculoPlaca': permanencia.veiculo.placa,
        'veiculoModelo': permanencia.veiculo.modelo,
        'vagaId': permanencia.vaga_id,
        'vagaNumero': permanencia.vaga.numero,
        'dataHoraEntrada': permanencia.data_hora_entrada.isoformat(),
        'dataHoraSaida': saida.isoformat() if saida is not None else None,
        'valorTotal': float(valor) if valor is not None else None,
        'status': permanencia.status,
    }


def entrada(request):
    if request.method != 'POST':
        response = JsonResponse({'error': 'Método não permitido'}, status=405)
        response['Allow'] = 'POST, OPTIONS'
        return response

    try:
        dados = json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    if not isinstance(dados, dict):
        return JsonResponse({'error': 'O corpo deve ser um objeto JSON'}, status=400)

    for campo in ('veiculoId', 'vagaId'):
        valor = dados.get(campo)
        if type(valor) is not int or not 1 <= valor <= 2**63 - 1:
            return JsonResponse({'error': f"Campo '{campo}' deve ser um ID inteiro positivo"}, status=400)

    try:
        permanencia = registrar_entrada(dados['veiculoId'], dados['vagaId'])
    except RecursoNaoEncontrado as erro:
        return JsonResponse({'error': str(erro)}, status=404)
    except ValueError as erro:
        return JsonResponse({'error': str(erro)}, status=409)

    return JsonResponse(permanencia_to_dict(permanencia), status=201)
