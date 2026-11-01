#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements/prod.txt

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input
