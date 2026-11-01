#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Installing Python dependencies..."
if command -v uv >/dev/null 2>&1; then
    echo "Using uv to install dependencies..."
    uv pip install --system -r requirements.txt
else
    echo "Using pip with --break-system-packages..."
    python3 -m pip install --break-system-packages -r requirements.txt || pip install --break-system-packages -r requirements.txt || pip install -r requirements.txt
fi

echo "==> Running database migrations..."
python3 manage.py migrate --noinput || python manage.py migrate --noinput || echo "Database migrations skipped."

echo "==> Collecting static files..."
python3 manage.py collectstatic --no-input || python manage.py collectstatic --no-input

echo "==> Build completed successfully!"
