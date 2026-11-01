from django.db.models import Count, Q
from django.http import JsonResponse
from ..models import Vaga, Permanencia 

def get_dashboard_data(request):
    vagas_stats = Vaga.objects.aggregate(
        total_vagas=Count('id'),
        vagas_livres=Count('id', filter=Q(status='LIVRE')),
        vagas_ocupadas=Count('id', filter=Q(status='OCUPADA'))
    )

    veiculos_estacionados = Permanencia.objects.filter(status='ABERTO').count()

    data = {
        "totalVagas": vagas_stats['total_vagas'] or 0,
        "vagasLivres": vagas_stats['vagas_livres'] or 0,
        "vagasOcupadas": vagas_stats['vagas_ocupadas'] or 0,
        "veiculosEstacionados": veiculos_estacionados
    }

    return JsonResponse(data, status=200)