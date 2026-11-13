import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo
from api.services.permanencia_service import calcular_valor


class CalculoValorTests(TestCase):
    def valor(self, **duracao):
        entrada = datetime(2026, 1, 1, 10, 0)
        return calcular_valor(entrada, entrada + timedelta(**duracao))

    def test_regras_de_cobranca(self):
        self.assertEqual(self.valor(minutes=0), Decimal('5.00'))      # mínimo de 1 hora
        self.assertEqual(self.valor(minutes=59), Decimal('5.00'))
        self.assertEqual(self.valor(minutes=60), Decimal('5.00'))
        self.assertEqual(self.valor(minutes=61), Decimal('10.00'))    # hora iniciada é cobrada
        self.assertEqual(self.valor(hours=2, seconds=59), Decimal('10.00'))  # segundos não contam
        self.assertEqual(self.valor(hours=5), Decimal('25.00'))


class PermanenciaTests(TestCase):
    def setUp(self):
        cliente = Cliente.objects.create(nome='Ana', cpf='111')
        self.veiculo = Veiculo.objects.create(
            placa='ABC-1234', marca='Fiat', modelo='Uno', cor='Azul', cliente=cliente,
        )
        self.vaga = Vaga.objects.get(numero='A01')

    def enviar(self, metodo, url, dados=None):
        corpo = json.dumps(dados) if dados is not None else ''
        return getattr(self.client, metodo)(url, corpo, content_type='application/json')

    def entrar(self, veiculo_id=None, vaga_id=None):
        return self.enviar('post', '/api/permanencias/entrada', {
            'veiculoId': veiculo_id or self.veiculo.id,
            'vagaId': vaga_id or self.vaga.id,
        })

    def test_fluxo_completo(self):
        entrada = self.entrar()
        self.assertEqual(entrada.status_code, 201)
        dados = entrada.json()
        self.assertEqual(
            (dados['veiculoPlaca'], dados['veiculoModelo'], dados['vagaNumero'], dados['status']),
            ('ABC-1234', 'Uno', 'A01', 'ABERTO'),
        )
        self.assertIsNone(dados['dataHoraSaida'])
        self.assertIsNone(dados['valorTotal'])
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, 'OCUPADA')

        saida = self.enviar('put', f"/api/permanencias/{dados['id']}/saida")
        self.assertEqual(saida.status_code, 200)
        self.assertEqual(saida.json()['valorTotal'], 5.0)
        self.assertEqual(saida.json()['status'], 'FINALIZADO')
        self.assertIsNotNone(saida.json()['dataHoraSaida'])
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, 'LIVRE')

        self.assertEqual(len(self.client.get('/api/permanencias?status=FINALIZADO').json()), 1)
        self.assertEqual(self.client.get('/api/permanencias/?status=ABERTO').json(), [])
        self.assertEqual(self.enviar('put', f"/api/permanencias/{dados['id']}/saida/").status_code, 409)

    def test_lista_mais_recentes_primeiro(self):
        outra = Vaga.objects.get(numero='A02')
        Permanencia.objects.create(veiculo=self.veiculo, vaga=self.vaga, status='FINALIZADO',
                                   data_hora_entrada=datetime(2026, 1, 1, 8))
        Permanencia.objects.create(veiculo=self.veiculo, vaga=outra, status='FINALIZADO',
                                   data_hora_entrada=datetime(2026, 1, 2, 8))
        numeros = [p['vagaNumero'] for p in self.client.get('/api/permanencias').json()]
        self.assertEqual(numeros, ['A02', 'A01'])

    def test_conflitos(self):
        self.entrar()
        outra_vaga = Vaga.objects.get(numero='A02')
        self.assertEqual(self.entrar(vaga_id=outra_vaga.id).status_code, 409)  # veículo já está dentro
        outro_cliente = Cliente.objects.create(nome='Bruno', cpf='222')
        outro = Veiculo.objects.create(placa='XYZ-9999', marca='VW', modelo='Gol', cor='Preto', cliente=outro_cliente)
        self.assertEqual(self.entrar(veiculo_id=outro.id).status_code, 409)  # vaga ocupada

    def test_inexistentes_nao_ocupam_vaga(self):
        self.assertEqual(self.entrar(veiculo_id=999).status_code, 404)
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, 'LIVRE')
        self.assertEqual(self.entrar(vaga_id=999).status_code, 404)
        self.assertEqual(self.enviar('put', '/api/permanencias/999/saida').status_code, 404)
        self.assertFalse(Permanencia.objects.exists())

    def test_campos_obrigatorios_e_json(self):
        url = '/api/permanencias/entrada'
        self.assertEqual(self.enviar('post', url, {'veiculoId': self.veiculo.id}).status_code, 400)
        self.assertEqual(self.enviar('post', url, {'veiculoId': True, 'vagaId': 1}).status_code, 400)
        self.assertEqual(self.enviar('post', url, {'veiculoId': '1', 'vagaId': 1}).status_code, 400)
        self.assertEqual(self.client.post(url, 'nao-json', content_type='application/json').status_code, 400)

    def test_metodos_nao_permitidos(self):
        self.assertEqual(self.client.get('/api/permanencias/entrada').status_code, 405)
        self.assertEqual(self.enviar('post', '/api/permanencias', {}).status_code, 405)
        self.assertEqual(self.client.get('/api/permanencias/1/saida').status_code, 405)

    def test_dashboard_conta_veiculos_estacionados(self):
        self.entrar()
        self.assertEqual(self.client.get('/api/dashboard').json(), {
            'totalVagas': 15, 'vagasLivres': 14, 'vagasOcupadas': 1, 'veiculosEstacionados': 1,
        })

    def test_exclusao_bloqueada_com_historico(self):
        self.entrar()
        self.assertEqual(self.client.delete(f'/api/veiculos/{self.veiculo.id}').status_code, 409)
        self.assertEqual(self.client.delete(f'/api/vagas/{self.vaga.id}').status_code, 409)
        self.assertEqual(self.client.delete(f'/api/clientes/{self.veiculo.cliente_id}').status_code, 409)
