import json
from functools import wraps

from django.http import JsonResponse


def json_response(data, status=200):
    """Retorna uma resposta JSON padronizada."""
    return JsonResponse(
        data,
        status=status,
        safe=isinstance(data, dict),
        json_dumps_params={"ensure_ascii": False},
    )


def error_response(message, status=400):
    """Retorna um erro no formato esperado pelo frontend."""
    return json_response({"error": str(message)}, status=status)


def message_response(message, status=200):
    """Retorna uma mensagem padronizada."""
    return json_response({"message": str(message)}, status=status)


def parse_json_body(request):
    """Lê o corpo da requisição e valida se contém um objeto JSON."""
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("O corpo da requisição contém um JSON inválido.") from exc

    if not isinstance(data, dict):
        raise ValueError("O corpo da requisição deve ser um objeto JSON.")

    return data


def validate_required_fields(data, fields):
    """Retorna a lista de campos obrigatórios ausentes ou vazios."""
    return [
        field
        for field in fields
        if field not in data
        or data[field] is None
        or (isinstance(data[field], str) and not data[field].strip())
    ]


def require_methods(*methods):
    """Restringe os métodos HTTP permitidos em uma view."""
    allowed = tuple(dict.fromkeys(method.upper() for method in methods))

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method not in allowed:
                response = error_response(
                    "Método não permitido.",
                    status=405,
                )
                response["Allow"] = ", ".join(
                    dict.fromkeys((*allowed, "OPTIONS"))
                )
                return response

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
