from django.db.models import Count, Q
from django.http import JsonResponse

from api.models import Permanencia, Vaga


def dashboard(request):
    if request.method != 'GET':
        response = JsonResponse({'error': 'Método não permitido'}, status=405)
        response['Allow'] = 'GET, OPTIONS'
        return response
    totais = Vaga.objects.aggregate(
        totalVagas=Count('id'),
        vagasLivres=Count('id', filter=Q(status=Vaga.Status.LIVRE)),
        vagasOcupadas=Count('id', filter=Q(status=Vaga.Status.OCUPADA)),
    )
    totais['veiculosEstacionados'] = Permanencia.objects.filter(
        status=Permanencia.Status.ABERTO
    ).count()
    return JsonResponse(totais)
