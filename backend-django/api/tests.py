import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from api.models import Cliente, Permanencia, Vaga, Veiculo
from api.services.permanencia_service import _calcular_valor


class VeiculoApiTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome='Maria Silva',
            cpf='123.456.789-00',
        )
        self.outro_cliente = Cliente.objects.create(
            nome='João Souza',
            cpf='987.654.321-00',
        )
        self.url = '/api/veiculos'
        self.dados = {
            'placa': 'ABC-1234',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'cor': 'Prata',
            'clienteId': self.cliente.id,
        }

    def enviar_json(self, metodo, url, dados=None):
        return getattr(self.client, metodo)(
            url,
            data=json.dumps(dados) if dados is not None else None,
            content_type='application/json',
        )

    def test_lista_veiculos_retorna_cliente_nome(self):
        Veiculo.objects.create(
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            cor='Prata',
            cliente=self.cliente,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['clienteNome'], 'Maria Silva')
        self.assertEqual(response.json()[0]['clienteId'], self.cliente.id)

    def test_cadastra_veiculo(self):
        response = self.enviar_json('post', self.url, self.dados)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['placa'], 'ABC-1234')
        self.assertEqual(response.json()['clienteNome'], 'Maria Silva')
        self.assertEqual(Veiculo.objects.count(), 1)

    def test_placa_e_normalizada_para_maiusculas(self):
        dados = {**self.dados, 'placa': 'abc-1234'}
        response = self.enviar_json('post', self.url, dados)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['placa'], 'ABC-1234')

    def test_placa_duplicada_retorna_409(self):
        self.enviar_json('post', self.url, self.dados)
        response = self.enviar_json('post', self.url, self.dados)
        self.assertEqual(response.status_code, 409)

    def test_cliente_inexistente_retorna_404(self):
        dados = {**self.dados, 'clienteId': 99999}
        response = self.enviar_json('post', self.url, dados)
        self.assertEqual(response.status_code, 404)

    def test_campos_obrigatorios_retorna_400(self):
        dados = {**self.dados}
        dados.pop('cor')
        response = self.enviar_json('post', self.url, dados)
        self.assertEqual(response.status_code, 400)

    def test_json_invalido_retorna_400(self):
        response = self.client.post(
            self.url, data='{invalido', content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_atualiza_veiculo(self):
        veiculo = Veiculo.objects.create(
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            cor='Prata',
            cliente=self.cliente,
        )
        dados = {
            **self.dados,
            'placa': 'XYZ-9876',
            'clienteId': self.outro_cliente.id,
        }
        response = self.enviar_json('put', f'{self.url}/{veiculo.id}', dados)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['placa'], 'XYZ-9876')
        self.assertEqual(response.json()['clienteNome'], 'João Souza')

    def test_atualizacao_com_placa_de_outro_veiculo_retorna_409(self):
        self.enviar_json('post', self.url, self.dados)
        segundo = {**self.dados, 'placa': 'DEF-5678'}
        response = self.enviar_json('post', self.url, segundo)
        segundo_id = response.json()['id']
        response = self.enviar_json('put', f'{self.url}/{segundo_id}', self.dados)
        self.assertEqual(response.status_code, 409)

    def test_atualizacao_de_veiculo_inexistente_retorna_404(self):
        response = self.enviar_json('put', f'{self.url}/99999', self.dados)
        self.assertEqual(response.status_code, 404)

    def test_exclui_veiculo(self):
        veiculo = Veiculo.objects.create(
            placa='ABC-1234',
            marca='Toyota',
            modelo='Corolla',
            cor='Prata',
            cliente=self.cliente,
        )
        response = self.client.delete(f'{self.url}/{veiculo.id}')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Veiculo.objects.filter(pk=veiculo.id).exists())

    def test_exclusao_de_veiculo_inexistente_retorna_404(self):
        response = self.client.delete(f'{self.url}/99999')
        self.assertEqual(response.status_code, 404)


class ClienteApiTests(TestCase):
    def criar(self, **alteracoes):
        dados = {'nome': 'Ana', 'cpf': '111.111.111-11', **alteracoes}
        return self.client.post('/api/clientes', dados, content_type='application/json')

    def test_crud_completo(self):
        response = self.criar()
        self.assertEqual(response.status_code, 201)
        id = response.json()['id']
        self.assertEqual(self.client.get(f'/api/clientes/{id}/').json()['nome'], 'Ana')
        response = self.client.put(
            f'/api/clientes/{id}', {'nome': 'Ana Silva', 'cpf': '111.111.111-11'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/clientes/').json()[0]['nome'], 'Ana Silva')
        self.assertEqual(self.client.delete(f'/api/clientes/{id}').status_code, 204)

    def test_obrigatorios_tipos_e_limites(self):
        for dados in ({}, {'nome': '  ', 'cpf': '1'}, {'nome': [], 'cpf': '1'},
                      {'nome': 'A' * 101, 'cpf': '1'}):
            with self.subTest(dados=dados):
                self.assertEqual(self.client.post(
                    '/api/clientes', dados, content_type='application/json'
                ).status_code, 400)

    def test_json_malformado_e_corpo_lista(self):
        for body in ('{', '[]', 'null'):
            self.assertEqual(self.client.post(
                '/api/clientes', body, content_type='application/json'
            ).status_code, 400)

    def test_cpf_duplicado_na_criacao_e_edicao(self):
        self.criar()
        self.assertEqual(self.criar().status_code, 409)
        outro = self.criar(cpf='222').json()
        self.assertEqual(self.client.put(
            f"/api/clientes/{outro['id']}", {'nome': 'Outro', 'cpf': '111.111.111-11'},
            content_type='application/json',
        ).status_code, 409)

    def test_inexistentes_e_metodos(self):
        for metodo in ('get', 'put', 'delete'):
            self.assertEqual(getattr(self.client, metodo)('/api/clientes/999').status_code, 404)
        self.assertEqual(self.client.patch('/api/clientes').status_code, 405)


class EstacionamentoApiTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome='Teste', cpf='123')
        self.veiculo = Veiculo.objects.create(
            cliente=self.cliente, placa='ABC1234', marca='Teste', modelo='Modelo', cor='Prata'
        )
        self.vaga = Vaga.objects.get(numero='A01')

    def entrada(self, veiculo=None, vaga=None):
        return self.client.post('/api/permanencias/entrada', {
            'veiculoId': self.veiculo.id if veiculo is None else veiculo,
            'vagaId': self.vaga.id if vaga is None else vaga,
        }, content_type='application/json')

    def test_vagas_iniciais_e_filtro(self):
        self.assertEqual(Vaga.objects.count(), 15)
        self.assertEqual(self.client.get('/api/vagas?status=LIVRE').status_code, 200)
        self.assertEqual(len(self.client.get('/api/vagas/').json()), 15)

    def test_crud_vaga_e_duplicidade(self):
        dados = {'numero': 'C01', 'tipo': 'MOTO'}
        criada = self.client.post('/api/vagas', dados, content_type='application/json')
        self.assertEqual(criada.status_code, 201)
        self.assertEqual(self.client.post(
            '/api/vagas', dados, content_type='application/json'
        ).status_code, 409)
        id = criada.json()['id']
        self.assertEqual(self.client.get(f'/api/vagas/{id}').status_code, 200)
        self.assertEqual(self.client.put(
            f'/api/vagas/{id}/', {'numero': 'C02', 'tipo': 'CARRO'}, content_type='application/json'
        ).status_code, 200)
        self.assertEqual(self.client.delete(f'/api/vagas/{id}').status_code, 204)

    def test_vaga_invalida_e_inexistente(self):
        for dados in ({}, {'numero': 'C1', 'tipo': 'OUTRO'},
                      {'numero': 'C1', 'tipo': 'MOTO', 'status': 'OUTRO'}):
            self.assertEqual(self.client.post(
                '/api/vagas', dados, content_type='application/json'
            ).status_code, 400)
        self.assertEqual(self.client.get('/api/vagas/999').status_code, 404)

    def test_dashboard_e_fluxo_completo(self):
        dashboard = self.client.get('/api/dashboard').json()
        self.assertEqual(dashboard, {
            'totalVagas': 15, 'vagasLivres': 15, 'vagasOcupadas': 0, 'veiculosEstacionados': 0,
        })
        entrada = self.entrada()
        self.assertEqual(entrada.status_code, 201)
        id = entrada.json()['id']
        self.assertEqual(self.client.get('/api/dashboard/').json()['vagasLivres'], 14)
        self.assertEqual(len(self.client.get('/api/permanencias?status=ABERTO').json()), 1)
        response = self.client.put(f'/api/permanencias/{id}/saida/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['valorTotal'], 5)
        self.assertEqual(len(self.client.get('/api/permanencias?status=FINALIZADO').json()), 1)
        self.assertEqual(self.client.get('/api/dashboard').json(), dashboard)

    def test_veiculo_ja_estacionado(self):
        self.entrada()
        self.assertEqual(self.entrada(vaga=Vaga.objects.get(numero='A02').id).status_code, 409)
        self.assertEqual(Vaga.objects.get(numero='A02').status, 'LIVRE')

    def test_vaga_ocupada(self):
        self.vaga.status = 'OCUPADA'
        self.vaga.save()
        self.assertEqual(self.entrada().status_code, 409)
        self.assertEqual(Permanencia.objects.count(), 0)

    def test_entrada_inexistentes_e_ids_invalidos(self):
        self.assertEqual(self.entrada(veiculo=999).status_code, 404)
        self.assertEqual(self.entrada(vaga=999).status_code, 404)
        for valor in (True, 0, -1, '1', None, 2**80):
            self.assertEqual(self.client.post('/api/permanencias/entrada', {
                'veiculoId': valor, 'vagaId': self.vaga.id
            }, content_type='application/json').status_code, 400)

    def test_historico_protege_exclusao_e_liberacao_manual(self):
        self.entrada()
        for recurso, id in (('clientes', self.cliente.id), ('veiculos', self.veiculo.id),
                             ('vagas', self.vaga.id)):
            self.assertEqual(self.client.delete(f'/api/{recurso}/{id}').status_code, 409)
        self.assertEqual(self.client.put(f'/api/vagas/{self.vaga.id}', {
            'numero': 'A01', 'tipo': 'CARRO', 'status': 'LIVRE',
        }, content_type='application/json').status_code, 409)

    def test_saida_repetida_e_inexistente(self):
        id = self.entrada().json()['id']
        self.assertEqual(self.client.put(f'/api/permanencias/{id}/saida').status_code, 200)
        self.assertEqual(self.client.put(f'/api/permanencias/{id}/saida').status_code, 409)
        self.assertEqual(self.client.put('/api/permanencias/999/saida').status_code, 404)

    def test_fracoes_e_limites_da_cobranca(self):
        inicio = timezone.now()
        for minutos, segundos, esperado in (
            (0, 0, '5.00'), (59, 59, '5.00'), (60, 0, '5.00'),
            (60, 1, '10.00'), (120, 0, '10.00'), (120, 1, '15.00'),
        ):
            self.assertEqual(
                _calcular_valor(inicio, inicio + timedelta(minutes=minutos, seconds=segundos)),
                Decimal(esperado),
            )

    def test_rollback_se_criacao_de_permanencia_falhar(self):
        with patch('api.services.permanencia_service.Permanencia.objects.create',
                   side_effect=RuntimeError('Falha simulada')):
            with self.assertRaises(RuntimeError):
                self.entrada()
        self.vaga.refresh_from_db()
        self.assertEqual(self.vaga.status, 'LIVRE')
        self.assertEqual(Permanencia.objects.count(), 0)

    def test_listagem_nao_faz_consulta_por_linha(self):
        self.entrada()
        with CaptureQueriesContext(connection) as consultas:
            self.assertEqual(self.client.get('/api/permanencias').status_code, 200)
        self.assertEqual(len(consultas), 1)

    def test_cors_em_sucesso_erro_e_preflight(self):
        for response in (
            self.client.get('/api/dashboard'),
            self.client.get('/api/clientes/999'),
            self.client.options('/api/permanencias/entrada'),
        ):
            self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        self.assertEqual(self.client.options('/api/clientes').status_code, 204)

    def test_consulta_individual_de_veiculo(self):
        response = self.client.get(f'/api/veiculos/{self.veiculo.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['clienteNome'], 'Teste')
