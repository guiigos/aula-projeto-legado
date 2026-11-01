.PHONY: up down restart build rebuild ps status logs logs-backend logs-frontend \
        logs-all logs-all-backend stop start shell migrate makemigrations check test clean

up:
	docker compose up -d

build:
	docker compose up -d --build

rebuild:
	docker compose up -d --build backend

restart:
	docker compose restart

logs:
	docker compose logs -f --tail=100

logs-backend:
	docker compose logs -f --tail=100 backend

logs-frontend:
	docker compose logs -f --tail=100 frontend

logs-all:
	docker compose logs -f

stop:
	docker compose stop

start:
	docker compose start

shell:
	docker compose exec backend sh

check:
	docker compose exec backend python manage.py check
