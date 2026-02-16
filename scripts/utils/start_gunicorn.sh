#!/bin/bash

start_gunicorn() {
    echo "Starting Gunicorn via Python module..."
    exec python -m gunicorn payout_service.wsgi:application \
        --workers="${WEB_CONCURRENCY:-2}" \
        --bind 0.0.0.0:8000 \
        --worker-tmp-dir /dev/shm \
        --access-logfile - \
        --error-logfile -
}
