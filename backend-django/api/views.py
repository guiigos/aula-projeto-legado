from django.http import JsonResponse


def status(request):
    if request.method != 'GET':
        response = JsonResponse({'error': 'Método não permitido'}, status=405)
        response['Allow'] = 'GET, OPTIONS'
        return response

    return JsonResponse({'status': 'ok'})
