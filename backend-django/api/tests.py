import json

from django.test import TestCase

from api.models import Cliente, Veiculo


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
