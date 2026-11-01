#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Preparing Python build environment..."

if command -v uv >/dev/null 2>&1; then
    echo "Using uv to manage Python 3.12 virtual environment..."
    uv venv .venv --python 3.12 || uv venv .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
else
    echo "Using pip to install dependencies..."
    python3 -m pip install --break-system-packages -r requirements.txt || pip install --break-system-packages -r requirements.txt || pip install -r requirements.txt
fi

echo "==> Running database migrations..."
python manage.py migrate --noinput || python3 manage.py migrate --noinput || echo "Database migrations skipped."

echo "==> Collecting static files..."
python manage.py collectstatic --no-input || python3 manage.py collectstatic --no-input

# Duplicate files under staticfiles/static/ to satisfy all Vercel static routing conventions
if [ -d "staticfiles" ]; then
    echo "==> Mirroring static assets for Vercel CDN..."
    mkdir -p staticfiles/static
    cp -r staticfiles/css staticfiles/js staticfiles/images staticfiles/admin staticfiles/static/ 2>/dev/null || true
fi

echo "==> Build completed successfully!"
