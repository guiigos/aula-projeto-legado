from datetime import datetime

from django.test import TestCase

from api.models import Cliente, Permanencia, Vaga, Veiculo


class CadastroTestCase(TestCase):
    def setUp(self):
        self.dados_cliente = {
            'nome': 'Ana Silva', 'cpf': '123.456.789-00',
            'telefone': '11999999999', 'email': 'ana@example.com',
        }
        self.cliente = Cliente.objects.create(**self.dados_cliente)
        self.dados_veiculo = {
            'placa': 'ABC-1234', 'marca': 'Toyota', 'modelo': 'Corolla',
            'cor': 'Branco', 'clienteId': self.cliente.pk,
        }
        self.veiculo = Veiculo.objects.create(
            placa='ABC-1234', marca='Toyota', modelo='Corolla',
            cor='Branco', cliente=self.cliente,
        )

    def enviar(self, metodo, url, dados):
        return getattr(self.client, metodo)(url, dados, content_type='application/json')

    def registrar_permanencia(self, status='ABERTO'):
        vaga = Vaga.objects.create(numero='T01', tipo='CARRO')
        return Permanencia.objects.create(
            veiculo=self.veiculo, vaga=vaga,
            data_hora_entrada=datetime(2026, 11, 13, 10), status=status,
        )


class ClientesTests(CadastroTestCase):
    def test_cadastrar_e_buscar_cliente(self):
        dados = {**self.dados_cliente, 'nome': 'Bruno', 'cpf': '987.654.321-00'}
        response = self.enviar('post', '/api/clientes/', dados)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'id': response.json()['id'], **dados})
        detalhe = self.client.get(f"/api/clientes/{response.json()['id']}/")
        self.assertEqual(detalhe.status_code, 200)
        self.assertEqual(detalhe.json(), response.json())

    def test_listar_ordenados_e_buscar_por_nome_ou_cpf(self):
        outro = Cliente.objects.create(nome='Bruno', cpf='987.654.321-00')
        response = self.client.get('/api/clientes/')
        self.assertEqual([c['id'] for c in response.json()], [self.cliente.pk, outro.pk])
        for busca in ('ana', '123.456'):
            with self.subTest(busca=busca):
                response = self.client.get('/api/clientes/', {'busca': busca})
                self.assertEqual([c['id'] for c in response.json()], [self.cliente.pk])
        self.assertEqual(self.client.get('/api/clientes/?busca=inexistente').json(), [])

    def test_opcionais_podem_ser_omitidos_nulos_ou_vazios(self):
        for indice, valor in enumerate((None, '')):
            dados = {'nome': 'Novo', 'cpf': f'cpf-{indice}', 'telefone': valor, 'email': valor}
            response = self.enviar('post', '/api/clientes/', dados)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json()['telefone'], valor)
            self.assertEqual(response.json()['email'], valor)
        response = self.enviar('post', '/api/clientes/', {'nome': 'Novo', 'cpf': 'cpf-3'})
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()['telefone'])
        self.assertIsNone(response.json()['email'])

    def test_atualizar_cliente_inclusive_manter_proprio_cpf(self):
        dados = {**self.dados_cliente, 'nome': 'Ana Souza'}
        response = self.enviar('put', f'/api/clientes/{self.cliente.pk}/', dados)
        self.assertEqual(response.status_code, 200)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nome, 'Ana Souza')
        self.assertEqual(response.json()['cpf'], dados['cpf'])

    def test_cpf_duplicado_no_cadastro_e_na_atualizacao(self):
        response = self.enviar('post', '/api/clientes/', self.dados_cliente)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {'error': 'CPF já cadastrado'})
        outro = Cliente.objects.create(nome='Bruno', cpf='987.654.321-00')
        response = self.enviar('put', f'/api/clientes/{outro.pk}/', self.dados_cliente)
        self.assertEqual(response.status_code, 409)
        outro.refresh_from_db()
        self.assertEqual(outro.nome, 'Bruno')
        self.assertEqual(outro.cpf, '987.654.321-00')

    def test_validar_obrigatorios_no_cadastro_e_na_atualizacao(self):
        for metodo, url in (('post', '/api/clientes/'), ('put', f'/api/clientes/{self.cliente.pk}/')):
            for campo in ('nome', 'cpf'):
                for valor in (None, '', '   ', 123, [], True):
                    with self.subTest(metodo=metodo, campo=campo, valor=valor):
                        response = self.enviar(metodo, url, {**self.dados_cliente, campo: valor})
                        self.assertEqual(response.status_code, 400)
                        self.assertIn('error', response.json())
        self.assertEqual(Cliente.objects.count(), 1)

    def test_validar_tipos_e_limites_inclusive_opcionais(self):
        for campo, limite in (('nome', 100), ('cpf', 14), ('telefone', 20), ('email', 100)):
            for valor in ('x' * (limite + 1), {}, 42):
                with self.subTest(campo=campo, valor=valor):
                    dados = {**self.dados_cliente, 'cpf': 'cpf-novo', campo: valor}
                    self.assertEqual(self.enviar('post', '/api/clientes/', dados).status_code, 400)

    def test_remover_espacos_dos_campos(self):
        dados = {'nome': ' Bruno ', 'cpf': ' 987.654.321-00 ', 'email': ' '}
        response = self.enviar('post', '/api/clientes/', dados)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['nome'], 'Bruno')
        self.assertEqual(response.json()['cpf'], '987.654.321-00')
        self.assertEqual(response.json()['email'], '')

    def test_cliente_inexistente(self):
        for metodo in ('get', 'put', 'delete'):
            with self.subTest(metodo=metodo):
                response = self.enviar(metodo, '/api/clientes/999999/', self.dados_cliente)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), {'error': 'Cliente não encontrado'})

    def test_excluir_cliente_sem_veiculos(self):
        outro = Cliente.objects.create(nome='Bruno', cpf='987.654.321-00')
        response = self.client.delete(f'/api/clientes/{outro.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertFalse(Cliente.objects.filter(pk=outro.pk).exists())

    def test_excluir_cliente_remove_veiculos_sem_permanencias(self):
        response = self.client.delete(f'/api/clientes/{self.cliente.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cliente.objects.filter(pk=self.cliente.pk).exists())
        self.assertFalse(Veiculo.objects.filter(pk=self.veiculo.pk).exists())

    def test_exclusao_com_historico_preserva_cliente_e_todos_os_veiculos(self):
        self.registrar_permanencia('FINALIZADO')
        outro = Veiculo.objects.create(
            placa='XYZ-9999', marca='Honda', modelo='Civic', cor='Preto', cliente=self.cliente,
        )
        response = self.client.delete(f'/api/clientes/{self.cliente.pk}/')
        self.assertEqual(response.status_code, 409)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())
        self.assertEqual(Veiculo.objects.filter(pk__in=(self.veiculo.pk, outro.pk)).count(), 2)
        self.assertEqual(Permanencia.objects.count(), 1)


class VeiculosTests(CadastroTestCase):
    def test_cadastrar_e_buscar_veiculo_com_nome_do_cliente(self):
        dados = {**self.dados_veiculo, 'placa': ' xyz-9876 '}
        response = self.enviar('post', '/api/veiculos/', dados)
        self.assertEqual(response.status_code, 201)
        esperado = {
            **dados, 'id': response.json()['id'], 'placa': 'XYZ-9876',
            'clienteNome': self.cliente.nome,
        }
        self.assertEqual(response.json(), esperado)
        detalhe = self.client.get(f"/api/veiculos/{response.json()['id']}/")
        self.assertEqual(detalhe.status_code, 200)
        self.assertEqual(detalhe.json(), esperado)

    def test_listagem_ordenada_sem_consultas_por_veiculo(self):
        Veiculo.objects.create(
            placa='AAA-1111', marca='Honda', modelo='Civic', cor='Preto', cliente=self.cliente,
        )
        with self.assertNumQueries(1):
            response = self.client.get('/api/veiculos/')
        self.assertEqual([v['placa'] for v in response.json()], ['AAA-1111', 'ABC-1234'])
        self.assertEqual(response.json()[0]['clienteNome'], self.cliente.nome)

    def test_buscar_veiculo_por_placa_modelo_ou_cliente(self):
        for busca in ('abc', 'Corolla', 'Ana'):
            with self.subTest(busca=busca):
                response = self.client.get('/api/veiculos/', {'busca': busca})
                self.assertEqual([v['id'] for v in response.json()], [self.veiculo.pk])
        self.assertEqual(self.client.get('/api/veiculos/?busca=inexistente').json(), [])

    def test_atualizar_veiculo_e_transferir_cliente(self):
        outro = Cliente.objects.create(nome='Bruno', cpf='987.654.321-00')
        dados = {**self.dados_veiculo, 'clienteId': outro.pk, 'cor': 'Azul'}
        response = self.enviar('put', f'/api/veiculos/{self.veiculo.pk}/', dados)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['clienteNome'], 'Bruno')
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.cliente_id, outro.pk)
        self.assertEqual(self.veiculo.cor, 'Azul')

    def test_placa_duplicada_no_cadastro_e_na_atualizacao(self):
        response = self.enviar('post', '/api/veiculos/', {**self.dados_veiculo, 'placa': 'abc-1234'})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {'error': 'Placa já cadastrada'})
        outro = Veiculo.objects.create(
            placa='XYZ-9999', marca='Honda', modelo='Civic', cor='Preto', cliente=self.cliente,
        )
        response = self.enviar('put', f'/api/veiculos/{outro.pk}/', self.dados_veiculo)
        self.assertEqual(response.status_code, 409)
        outro.refresh_from_db()
        self.assertEqual(outro.placa, 'XYZ-9999')
        self.assertEqual(outro.modelo, 'Civic')

    def test_validar_campos_textuais_obrigatorios_e_limites(self):
        for metodo, url in (('post', '/api/veiculos/'), ('put', f'/api/veiculos/{self.veiculo.pk}/')):
            for campo, limite in (('placa', 10), ('marca', 50), ('modelo', 50), ('cor', 30)):
                for valor in (None, '', ' ', True, 123, {}, 'x' * (limite + 1)):
                    with self.subTest(metodo=metodo, campo=campo, valor=valor):
                        dados = {**self.dados_veiculo, campo: valor}
                        self.assertEqual(self.enviar(metodo, url, dados).status_code, 400)
        self.assertEqual(Veiculo.objects.count(), 1)

    def test_validar_cliente_id_sem_converter_booleanos_ou_fracoes(self):
        for metodo, url in (('post', '/api/veiculos/'), ('put', f'/api/veiculos/{self.veiculo.pk}/')):
            for valor in (None, '', ' ', 0, -1, True, 1.5, '1', [], {}, 2**63):
                with self.subTest(metodo=metodo, valor=valor):
                    dados = {**self.dados_veiculo, 'clienteId': valor}
                    self.assertEqual(self.enviar(metodo, url, dados).status_code, 400)

    def test_cliente_inexistente_no_cadastro_e_atualizacao(self):
        for metodo, url in (('post', '/api/veiculos/'), ('put', f'/api/veiculos/{self.veiculo.pk}/')):
            response = self.enviar(metodo, url, {**self.dados_veiculo, 'clienteId': 999999})
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {'error': 'Cliente não encontrado'})
        self.veiculo.refresh_from_db()
        self.assertEqual(self.veiculo.cliente_id, self.cliente.pk)
        self.assertEqual(Veiculo.objects.count(), 1)

    def test_veiculo_inexistente(self):
        for metodo in ('get', 'put', 'delete'):
            response = self.enviar(metodo, '/api/veiculos/999999/', self.dados_veiculo)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json(), {'error': 'Veículo não encontrado'})

    def test_excluir_veiculo_sem_permanencias(self):
        response = self.client.delete(f'/api/veiculos/{self.veiculo.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertFalse(Veiculo.objects.filter(pk=self.veiculo.pk).exists())
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_bloquear_exclusao_com_permanencia_aberta_ou_finalizada(self):
        permanencia = self.registrar_permanencia()
        for status in ('ABERTO', 'FINALIZADO'):
            permanencia.status = status
            permanencia.save()
            response = self.client.delete(f'/api/veiculos/{self.veiculo.pk}/')
            self.assertEqual(response.status_code, 409)
            self.assertTrue(Veiculo.objects.filter(pk=self.veiculo.pk).exists())
            self.assertTrue(Permanencia.objects.filter(pk=permanencia.pk).exists())


class ContratoHttpTests(CadastroTestCase):
    def test_json_invalido_ou_fora_do_formato(self):
        for metodo, url in (
            ('post', '/api/clientes/'), ('put', f'/api/clientes/{self.cliente.pk}/'),
            ('post', '/api/veiculos/'), ('put', f'/api/veiculos/{self.veiculo.pk}/'),
        ):
            for corpo in (b'', b'{', b'[]', b'null', b'123', b'"texto"', b'\xff'):
                with self.subTest(metodo=metodo, url=url, corpo=corpo):
                    response = self.enviar(metodo, url, corpo)
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('error', response.json())

    def test_rotas_sem_barra_do_frontend_aceitam_todo_o_crud(self):
        for recurso, dados in (
            ('clientes', {**self.dados_cliente, 'cpf': '987.654.321-00'}),
            ('veiculos', {**self.dados_veiculo, 'placa': 'XYZ-9999'}),
        ):
            with self.subTest(recurso=recurso):
                base = f'/api/{recurso}'
                response = self.enviar('post', base, dados)
                self.assertEqual(response.status_code, 201)
                detalhe = f"{base}/{response.json()['id']}"
                self.assertEqual(self.client.get(base).status_code, 200)
                self.assertEqual(self.client.get(detalhe).status_code, 200)
                self.assertEqual(self.enviar('put', detalhe, dados).status_code, 200)
                self.assertEqual(self.client.delete(detalhe).status_code, 200)

    def test_metodos_nao_permitidos_retornam_json_e_allow(self):
        for recurso, id in (('clientes', self.cliente.pk), ('veiculos', self.veiculo.pk)):
            for metodo, url in (
                ('put', f'/api/{recurso}/'), ('delete', f'/api/{recurso}/'),
                ('post', f'/api/{recurso}/{id}/'), ('patch', f'/api/{recurso}/{id}/'),
            ):
                with self.subTest(metodo=metodo, url=url):
                    response = self.enviar(metodo, url, {})
                    self.assertEqual(response.status_code, 405)
                    self.assertIn('error', response.json())
                    self.assertIn('OPTIONS', response['Allow'])

    def test_cors_no_sucesso_erro_e_preflight(self):
        for response in (
            self.client.get('/api/clientes/'),
            self.client.get('/api/veiculos/999999/'),
            self.enviar('post', '/api/clientes/', {}),
            self.enviar('post', '/api/veiculos/', self.dados_veiculo),
            self.client.patch('/api/clientes/'),
            self.client.options('/api/veiculos/'),
        ):
            self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        self.assertEqual(self.client.options('/api/veiculos/').status_code, 204)
