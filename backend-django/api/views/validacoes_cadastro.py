from api.utils import validate_required_fields


def validar_textos(data, model, obrigatorios, opcionais=()):
    """Valida os tipos e limites dos campos antes de gravar no SQLite."""
    ausentes = validate_required_fields(data, obrigatorios)
    if ausentes:
        raise ValueError(f"Campo '{ausentes[0]}' é obrigatório")

    dados = {}
    for campo in (*obrigatorios, *opcionais):
        valor = data.get(campo)
        if valor is None and campo in opcionais:
            dados[campo] = None
            continue
        if not isinstance(valor, str):
            raise ValueError(f"Campo '{campo}' deve ser um texto")
        valor = valor.strip()
        limite = model._meta.get_field(campo).max_length
        if len(valor) > limite:
            raise ValueError(f"Campo '{campo}' deve ter no máximo {limite} caracteres")
        dados[campo] = valor
    return dados


def validar_cliente_id(valor):
    if valor is None or valor == '':
        raise ValueError("Campo 'clienteId' é obrigatório")
    if type(valor) is not int or not 0 < valor <= 9223372036854775807:
        raise ValueError("Campo 'clienteId' deve ser um inteiro positivo válido")
    return valor
