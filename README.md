Run this:

(Terminal 1)
c
# 4. Download AI model (first time only)
python download_model.py

# 1. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies (if not already done)
pip install -r requirements.txt

# 4. Download AI model (first time only)
python download_model.py

# 5. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 6. Start Redis server (Terminal 1)
redis-server

# 7. Start Django development server (Terminal 2)
python manage.py runserver

# 8. Start Celery worker (Terminal 3)
celery -A slaq_project worker --pool=solo -l info
