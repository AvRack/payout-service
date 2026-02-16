# Переменные
DC = docker compose
EXEC = $(DC) exec app
MANAGE = python manage.py

.PHONY: help up down restart migrate build test worker-logs superuser shell

help: ## Справка по командам
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Запустить все сервисы (app, db, redis, worker, nginx)
	$(DC) up -d

down: ## Остановить и удалить контейнеры
	$(DC) down

restart: down up ## Перезапустить все сервисы

build: ## Пересобрать образы
	$(DC) build

migrate: ## Создать и применить миграции
	$(EXEC) $(MANAGE) makemigrations
	$(EXEC) $(MANAGE) migrate

test: ## Запустить тесты приложения (pytest)
	$(EXEC) pytest -v

test-cov: ## Запустить тесты с проверкой покрытия кода
	$(EXEC) pytest --cov=. --cov-report=term-missing

worker-logs: ## Посмотреть логи воркера (Celery)
	$(DC) logs -f worker

superuser: ## Создать суперпользователя Django
	$(EXEC) $(MANAGE) createsuperuser

shell: ## Зайти в shell Django
	$(EXEC) $(MANAGE) shell
