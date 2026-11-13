# Sistema de Estacionamento

Aplicação web para gerenciamento de estacionamento, migrada de Java 8 para Python + Django.

- **Backend**: Python 3.11 + Django (views, ORM e migrations, sem outras bibliotecas)
- **Frontend**: HTML5, CSS3 e JavaScript puro, servido pelo Nginx
- **Banco de dados**: SQLite, criado pelo `python manage.py migrate`
- **Infraestrutura**: Docker Compose

## Executar com Docker

```bash
docker compose up --build -d
```

| Serviço     | Endereço              |
|-------------|-----------------------|
| Frontend    | http://localhost:3000 |
| Backend API | http://localhost:8080 |

O banco fica no volume `sqlite_data` e persiste entre reinicializações. Para parar os containers:

```bash
docker compose down
```

Para apagar também os dados, use `docker compose down -v`.

## Executar sem Docker

Dentro de `backend-django/`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8080
```

No Mac ou Linux, ative o ambiente com `source .venv/bin/activate`.

O frontend usa URLs relativas (`/api/...`), então precisa do Nginx para encaminhar as chamadas. Em `frontend/nginx.conf`, troque `backend:8080` por `127.0.0.1:8080`. Depois rode, dentro de `frontend/`:

```bash
nginx -p . -c nginx.conf
```

## Testes

Dentro de `backend-django/`:

```bash
python manage.py test api
```

## Estrutura

```
├── backend-django/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── estacionamento/      configurações, URLs e middleware de CORS
│   └── api/
│       ├── models.py
│       ├── urls.py
│       ├── utils.py         respostas JSON e validação de métodos
│       ├── serializers.py
│       ├── tests/           testes por funcionalidade
│       ├── migrations/      schema e vagas iniciais
│       ├── views/           endpoints
│       └── services/        regras de negócio de permanência
├── frontend/
└── docker-compose.yml
```

## API REST

A barra final das URLs é opcional.

| Método             | Endpoint                       | Descrição                              |
|--------------------|--------------------------------|----------------------------------------|
| GET                | /api/dashboard/                | Indicadores gerais                     |
| GET, POST          | /api/clientes/                 | Listar e cadastrar clientes            |
| GET, PUT, DELETE   | /api/clientes/{id}/            | Buscar, atualizar e excluir cliente    |
| GET, POST          | /api/veiculos/                 | Listar e cadastrar veículos            |
| GET, PUT, DELETE   | /api/veiculos/{id}/            | Buscar, atualizar e excluir veículo    |
| GET, POST          | /api/vagas/                    | Listar (`?status=LIVRE`) e cadastrar   |
| GET, PUT, DELETE   | /api/vagas/{id}/               | Buscar, atualizar e excluir vaga       |
| POST               | /api/permanencias/entrada/     | Registrar entrada                      |
| PUT                | /api/permanencias/{id}/saida/  | Registrar saída                        |
| GET                | /api/permanencias/             | Listar (`?status=ABERTO`)              |

## Regras de negócio

- Tarifa de **R$ 5,00 por hora**, com mínimo de 1 hora e frações arredondadas para cima
- Entrada bloqueada (409) se o veículo já estiver estacionado ou se a vaga estiver ocupada
- CPF, placa ou número de vaga duplicados retornam 409
- Recursos inexistentes retornam 404
- Veículos e vagas com permanências registradas não podem ser excluídos (409)
