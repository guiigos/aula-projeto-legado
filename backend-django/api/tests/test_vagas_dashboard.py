from datetime import datetime

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo


class VagasDashboardTestCase(TestCase):
    def enviar(self, metodo, url, dados):
        return getattr(self.client, metodo)(url, dados, content_type='application/json')


class VagasTests(VagasDashboardTestCase):
    def test_vagas_iniciais_ordenadas_e_filtro_por_status(self):
        vagas = self.client.get('/api/vagas').json()
        self.assertEqual(len(vagas), 15)
        self.assertEqual(vagas[0]['numero'], 'A01')
        Vaga.objects.filter(numero='A01').update(status='OCUPADA')
        ocupadas = self.client.get('/api/vagas?status=OCUPADA').json()
        self.assertEqual([v['numero'] for v in ocupadas], ['A01'])
        self.assertEqual(len(self.client.get('/api/vagas/?status=LIVRE').json()), 14)

    def test_cadastrar_sempre_livre_buscar_e_atualizar(self):
        response = self.enviar('post', '/api/vagas', {'numero': 'C01', 'tipo': 'CARRO', 'status': 'OCUPADA'})
        self.assertEqual(response.status_code, 201)
        vaga = response.json()
        self.assertEqual((vaga['numero'], vaga['tipo'], vaga['status']), ('C01', 'CARRO', 'LIVRE'))
        self.assertEqual(self.client.get(f"/api/vagas/{vaga['id']}").json(), vaga)

        atualizada = self.enviar('put', f"/api/vagas/{vaga['id']}/", {'numero': 'C01', 'tipo': 'MOTO', 'status': 'OCUPADA'})
        self.assertEqual(atualizada.status_code, 200)
        self.assertEqual((atualizada.json()['tipo'], atualizada.json()['status']), ('MOTO', 'OCUPADA'))
        invalido = self.enviar('put', f"/api/vagas/{vaga['id']}", {'numero': 'C01', 'tipo': 'MOTO', 'status': 'X'})
        self.assertEqual(invalido.json()['status'], 'LIVRE')

    def test_validacoes(self):
        self.assertEqual(self.enviar('post', '/api/vagas', {'tipo': 'CARRO'}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/vagas', {'numero': 'C02', 'tipo': 'BARCO'}).status_code, 400)
        self.assertEqual(self.enviar('post', '/api/vagas', {'numero': 'X' * 11, 'tipo': 'CARRO'}).status_code, 400)
        self.assertEqual(self.client.post('/api/vagas', 'nao-json', content_type='application/json').status_code, 400)
        self.assertEqual(self.enviar('post', '/api/vagas', {'numero': 'A01', 'tipo': 'CARRO'}).status_code, 409)
        self.assertEqual(self.client.get('/api/vagas/999').status_code, 404)
        self.assertEqual(self.client.patch('/api/vagas/1').status_code, 405)

    def test_excluir_vaga(self):
        vaga = Vaga.objects.get(numero='B05')
        response = self.client.delete(f'/api/vagas/{vaga.id}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vaga.objects.filter(pk=vaga.id).exists())

    def test_excluir_vaga_com_permanencia_retorna_409(self):
        cliente = Cliente.objects.create(nome='Ana', cpf='111')
        veiculo = Veiculo.objects.create(placa='ABC-1234', marca='Fiat', modelo='Uno', cor='Azul', cliente=cliente)
        vaga = Vaga.objects.get(numero='A01')
        Permanencia.objects.create(veiculo=veiculo, vaga=vaga, data_hora_entrada=datetime(2026, 11, 13, 10))
        self.assertEqual(self.client.delete(f'/api/vagas/{vaga.id}').status_code, 409)
        self.assertTrue(Vaga.objects.filter(pk=vaga.id).exists())


class DashboardTests(VagasDashboardTestCase):
    def test_contadores(self):
        self.assertEqual(self.client.get('/api/dashboard').json(), {
            'totalVagas': 15, 'vagasLivres': 15, 'vagasOcupadas': 0, 'veiculosEstacionados': 0,
        })
        cliente = Cliente.objects.create(nome='Ana', cpf='111')
        veiculo = Veiculo.objects.create(placa='ABC-1234', marca='Fiat', modelo='Uno', cor='Azul', cliente=cliente)
        vaga = Vaga.objects.get(numero='A01')
        vaga.status = 'OCUPADA'
        vaga.save()
        Permanencia.objects.create(veiculo=veiculo, vaga=vaga, data_hora_entrada=datetime(2026, 11, 13, 10))
        self.assertEqual(self.client.get('/api/dashboard/').json(), {
            'totalVagas': 15, 'vagasLivres': 14, 'vagasOcupadas': 1, 'veiculosEstacionados': 1,
        })

    def test_somente_get(self):
        self.assertEqual(self.enviar('post', '/api/dashboard', {}).status_code, 405)
