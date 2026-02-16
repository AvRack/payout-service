#!/bin/bash

set -o errexit
set -o nounset

wait_db() {
  echo "### Waiting for DB via Django Check ###"
  start_ts=$(date +%s)
  timeout="${BASH_WAIT_DB_TIMEOUT:-60}"

  # Пытаемся выполнить простую команду в БД через Django
  until python manage.py shell -c "from django.db import connection; connection.cursor()" &> /dev/null; do
    now_ts=$(date +%s)
    if [ $(( now_ts - start_ts )) -gt "$timeout" ]; then
        echo "Timeout: Database not available after $timeout seconds"
        exit 1
    fi
    echo "Django is waiting for DB connection..."
    sleep 2
  done
  echo "Database is ready and Django can connect!"
}

sync() {
  wait_db

  echo -e "\n### Running Migrations ###\n"
  python manage.py migrate --noinput

  echo -e "\n### DB Sync Completed ###\n"
}
