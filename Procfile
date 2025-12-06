# Procfile for Render/Heroku deployment
web: gunicorn slaq_project.wsgi:application --workers 3 --timeout 120
worker: celery -A slaq_project worker --loglevel=info --concurrency=2
