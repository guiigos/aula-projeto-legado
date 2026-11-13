from django.http import JsonResponse


def nao_encontrado(request, exception):
    """Retorna uma resposta JSON quando a rota não existe."""
    return JsonResponse(
        {"error": "A rota solicitada não foi encontrada."},
        status=404
    )


def erro_interno(request):
    """Retorna uma resposta JSON quando ocorre um erro interno."""
    return JsonResponse(
        {"error": "Ocorreu um erro interno no servidor."},
        status=500
    )
