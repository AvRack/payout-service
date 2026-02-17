[![codecov](https://codecov.io/gh/AvRack/payout-service/graph/badge.svg?token=I105B7271Z)](https://codecov.io/gh/AvRack/payout-service)
# Payout Service

## 🛠 Технологический стек
*   **Backend**: Python 3.12, Django 5.0, DRF
*   **Task Queue**: Celery + Redis
*   **Database**: PostgreSQL
*   **Web Server**: Nginx (Reverse Proxy) + Gunicorn
*   **Dev**: Docker Compose, GitHub Actions (CI), Ruff (Linter/Formatter)

---

## 🚀 Быстрый старт (Development)

Для локальной разработки используйте команды `make`:

1.  **Подготовка окружения**:
    ```bash
    make install  # Установит зависимости через uv и настроит pre-commit хуки
    ```
2.  **Запуск проекта**:
    ```bash
    make build    # Сборка образов
    make up       # Запуск всех контейнеров (App, DB, Redis, Worker, Nginx)
    ```
3.  **Миграции и доступ**:
    ```bash
    make migrate      # Создание таблиц в БД
    make superuser    # Создание админа (admin/admin)
    ```
    Проект будет доступен по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)

4.  **Тестирование и линтинг**:
    ```bash
    make test         # Запуск Pytest
    make test-cov     # Запуск тестов с отчетом о покрытии
    make lint         # Проверка кода Ruff
  