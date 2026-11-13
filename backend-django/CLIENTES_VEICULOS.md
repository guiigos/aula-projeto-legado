# Pessoa 4 — Clientes e veículos

Esta etapa usa os models existentes e os utilitários de `api.utils` e
`api.serializers` da etapa de infraestrutura (`feat/api-infraestrutura`).
O frontend e os models não precisam de alterações.

## Endpoints

| Métodos | URL | Operação |
| --- | --- | --- |
| GET / POST | `/api/clientes/` | Listar / cadastrar clientes |
| GET / PUT / DELETE | `/api/clientes/<id>/` | Buscar / atualizar / excluir cliente |
| GET / POST | `/api/veiculos/` | Listar / cadastrar veículos |
| GET / PUT / DELETE | `/api/veiculos/<id>/` | Buscar / atualizar / excluir veículo |

As mesmas URLs funcionam sem barra final, como o frontend legado utiliza,
sem redirecionar requisições de escrita.

`GET /api/clientes/?busca=Ana` pesquisa por nome ou CPF.
`GET /api/veiculos/?busca=ABC` pesquisa por placa, marca, modelo, cor ou nome
do cliente. Sem filtro, as listagens retornam todos os registros, ordenados
por nome do cliente ou placa do veículo.

## Dados e regras

Cliente: `nome` e `cpf` são textos obrigatórios; `telefone` e `email` são
opcionais. Veículo: `placa`, `marca`, `modelo` e `cor` são textos obrigatórios;
`clienteId` deve ser um inteiro positivo referente a um cliente existente.
Os limites de tamanho seguem os models. Espaços nas extremidades são removidos
e placas são convertidas para maiúsculas. PUT exige todos os campos obrigatórios;
os campos opcionais omitidos do cliente são definidos como `null`.

As respostas de veículos incluem `clienteId` e `clienteNome`. A consulta usa
`select_related('cliente')` para carregar os clientes junto com os veículos.

- Cadastro: HTTP 201; consulta, atualização e exclusão: HTTP 200.
- JSON inválido, tipos inválidos ou campos ausentes: HTTP 400.
- Cliente ou veículo inexistente, inclusive cliente vinculado ao veículo: HTTP 404.
- CPF ou placa duplicados, tanto no cadastro quanto na atualização: HTTP 409.
- Métodos não permitidos: HTTP 405, com JSON e cabeçalho `Allow`.
- Erros retornam `{"error": "mensagem"}` e exclusões retornam `{"message": "mensagem"}`.

A exclusão segue o schema legado e os models: cliente sem histórico é excluído
com seus veículos em cascata. Permanências abertas ou finalizadas impedem a
exclusão do veículo e, por consequência, do cliente, retornando HTTP 409.
As operações de gravação e exclusão usam transações para evitar alterações parciais.

## Executar e testar

Com Python 3.11+ e o ambiente virtual ativado, na pasta `backend-django`:

```sh
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8080
```

Executar os testes desta etapa (utilizam banco de teste separado):

```sh
python manage.py test api.tests.test_clientes_veiculos
```

As rotas de vagas, dashboard e permanências serão integradas nas etapas dos
respectivos responsáveis.
