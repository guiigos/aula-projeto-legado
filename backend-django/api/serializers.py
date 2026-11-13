def serialize_cliente(cliente):
    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "telefone": cliente.telefone,
        "email": cliente.email,
    }


def serialize_veiculo(veiculo):
    return {
        "id": veiculo.id,
        "placa": veiculo.placa,
        "marca": veiculo.marca,
        "modelo": veiculo.modelo,
        "cor": veiculo.cor,
        "clienteId": veiculo.cliente_id,
        "clienteNome": veiculo.cliente.nome,
    }


def serialize_vaga(vaga):
    return {
        "id": vaga.id,
        "numero": vaga.numero,
        "tipo": vaga.tipo,
        "status": vaga.status,
    }


def serialize_permanencia(permanencia):
    return {
        "id": permanencia.id,
        "veiculoId": permanencia.veiculo_id,
        "veiculoPlaca": permanencia.veiculo.placa,
        "veiculoModelo": permanencia.veiculo.modelo,
        "vagaId": permanencia.vaga_id,
        "vagaNumero": permanencia.vaga.numero,
        "dataHoraEntrada": permanencia.data_hora_entrada.isoformat(),
        "dataHoraSaida": (
            permanencia.data_hora_saida.isoformat()
            if permanencia.data_hora_saida
            else None
        ),
        "valorTotal": (
            float(permanencia.valor_total)
            if permanencia.valor_total is not None
            else None
        ),
        "status": permanencia.status,
    }
