from api.models import Permanencia, Vaga
from api.utils import json_response, require_methods


@require_methods('GET')
def dashboard(request):
    return json_response({
        'totalVagas': Vaga.objects.count(),
        'vagasLivres': Vaga.objects.filter(status='LIVRE').count(),
        'vagasOcupadas': Vaga.objects.filter(status='OCUPADA').count(),
        'veiculosEstacionados': Permanencia.objects.filter(status='ABERTO').count(),
    })
