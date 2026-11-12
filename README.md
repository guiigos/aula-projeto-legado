# Sistema de Estacionamento

Backend migrado de Java 8 para Python 3.11 e Django 5.2, com SQLite.
O frontend HTML, CSS e JavaScript original usa a API pelo proxy Nginx.

## Executar com Docker

Com o Docker Desktop aberto, na raiz do projeto:

```bash
docker compose up --build -d
```

- Frontend em http://localhost:3000
- API em http://localhost:8080/api/status
- Dois serviços, backend Django e frontend Nginx.

O backend executa `python manage.py migrate --noinput` na inicialização.
As migrations criam as tabelas e as 15 vagas iniciais (A01–A10 e B01–B05).
O volume `sqlite_data` guarda o arquivo `/app/data/db.sqlite3`.

```bash
docker compose restart
docker compose logs -f backend
docker compose down
```

`restart` e `down` preservam o volume. `docker compose down -v` apaga o banco SQLite.

## Executar o backend localmente

Requer Python 3.11 ou superior. Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend-django/requirements.txt
cd backend-django
python manage.py migrate
python manage.py runserver 8080
```

No Windows, ative o ambiente com `.venv\Scripts\activate` no lugar do comando `source`.

O frontend usa URLs relativas. Para usar as telas, prefira o Docker com Nginx.
O servidor Django local fornece a API. Pare o backend Docker antes de usar a mesma porta localmente.

## Testes

```bash
cd backend-django
../.venv/bin/python manage.py check
../.venv/bin/python manage.py makemigrations --check --dry-run
../.venv/bin/python manage.py test api
```

No Windows, com o ambiente ativado, use `python manage.py ...`.

Os testes usam um banco separado. Cobrem CRUD, duplicidades, recursos inexistentes,
relacionamentos, CORS, dashboard, entrada, saída, cobrança e rollback.

## Estrutura

```text
backend-django/
  api/
    models.py
    migrations/
    views/
    services/permanencia_service.py
  estacionamento/
    settings.py
    urls.py
    middleware.py
  manage.py
  requirements.txt
  Dockerfile
frontend/
docker-compose.yml
```

`backend/` e `database/` guardam a implementação Java e o SQL de referência.
O Compose usa `backend-django/`.

## API REST

| Método | Endpoint                        | Descrição               |
|--------|---------------------------------|-------------------------|
| GET    | /api/dashboard                  | Indicadores gerais      |
| GET    | /api/clientes                   | Listar clientes         |
| GET    | /api/clientes/{id}              | Buscar cliente          |
| POST   | /api/clientes                   | Cadastrar cliente       |
| PUT    | /api/clientes/{id}              | Atualizar cliente       |
| DELETE | /api/clientes/{id}              | Excluir cliente         |
| GET    | /api/veiculos                   | Listar veículos         |
| GET    | /api/veiculos/{id}              | Buscar veículo          |
| POST   | /api/veiculos                   | Cadastrar veículo       |
| PUT    | /api/veiculos/{id}              | Atualizar veículo       |
| DELETE | /api/veiculos/{id}              | Excluir veículo         |
| GET    | /api/vagas                      | Listar vagas            |
| GET    | /api/vagas?status=LIVRE         | Listar vagas livres     |
| POST   | /api/vagas                      | Cadastrar vaga          |
| PUT    | /api/vagas/{id}                 | Atualizar vaga          |
| DELETE | /api/vagas/{id}                 | Excluir vaga            |
| POST   | /api/permanencias/entrada       | Registrar entrada       |
| PUT    | /api/permanencias/{id}/saida    | Registrar saída         |
| GET    | /api/permanencias               | Listar permanências     |
| GET    | /api/permanencias?status=ABERTO | Listar abertas          |

---

## Regras de negócio

- Tarifa de R$ 5,00 por hora, mínimo de uma hora e frações arredondadas para cima.
- Cálculo monetário com `Decimal` e persistência com `DecimalField`.
- Veículo com permanência aberta e vaga ocupada bloqueiam uma nova entrada.
- Entrada e saída usam `transaction.atomic` para confirmar as alterações em conjunto.
- O SQLite usa transações `IMMEDIATE` para coordenar requisições concorrentes.
- O histórico protege a exclusão de veículos e vagas associados.
- Uma vaga com permanência aberta deve ser liberada pelo registro de saída.
- Campos obrigatórios e JSON inválido retornam 400, inexistentes 404 e conflitos 409.
- A API aceita URLs com e sem barra final e usa os campos JSON esperados pelas telas.
- CORS e preflight OPTIONS são implementados por middleware.
- O projeto usa Django e a biblioteca padrão do Python, com as dependências internas do Django.
- As views verificam os métodos HTTP manualmente e usam serialização manual.
- Datas usam `USE_TZ = False` e `America/Sao_Paulo`.

## Ambiente de desenvolvimento

O Docker usa o servidor de desenvolvimento do Django, conforme a atividade.
`DB_PATH` permite mudar o caminho do SQLite.
`DJANGO_SECRET_KEY` permite definir a chave do projeto.
O banco local e o ambiente virtual ficam fora do Git.
