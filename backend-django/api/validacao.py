import json


def ler_json(request):
    try:
        dados = json.loads(request.body)
    except ValueError:
        raise ValueError('JSON inválido') from None
    if not isinstance(dados, dict):
        raise ValueError('O corpo deve ser um objeto JSON')
    return dados


def texto(dados, campo, limite, obrigatorio=True):
    valor = dados.get(campo)
    if valor is None and not obrigatorio:
        return None
    if not isinstance(valor, str):
        raise ValueError(f"Campo '{campo}' deve ser um texto")
    valor = valor.strip()
    if obrigatorio and not valor:
        raise ValueError(f"Campo '{campo}' é obrigatório")
    if len(valor) > limite:
        raise ValueError(f"Campo '{campo}' deve ter no máximo {limite} caracteres")
    return valor
