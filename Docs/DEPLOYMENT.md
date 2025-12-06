# SLAQ Deployment Guide

This guide covers deploying the SLAQ stuttering analysis application to production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Supabase Setup](#supabase-setup)
5. [Deployment Options](#deployment-options)
   - [Render](#render)
   - [Railway](#railway)
   - [AWS](#aws)
   - [Docker](#docker)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.10+
- PostgreSQL database (managed or self-hosted)
- Redis instance (for Celery task queue)
- Supabase project (for storage)
- ffmpeg installed on the server (for audio processing)

## Environment Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example.template .env
   ```

2. **Generate a new Django secret key:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Configure all required environment variables** (see `.env.example.template`)

4. **Never commit `.env` files** - they are in `.gitignore`

---

## Database Setup

### Using DATABASE_URL (Recommended)

Set a single `DATABASE_URL` environment variable:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Individual Settings

If not using `DATABASE_URL`, set:
```
DB_NAME=slaq_d_db
DB_USER=your_user
DB_USER_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
```

### Run Migrations

```bash
python manage.py migrate
```

---

## Supabase Setup

1. **Create a Supabase project** at https://supabase.com

2. **Get your API keys** from Settings → API:
   - `SUPABASE_URL`: Your project URL
   - `SUPABASE_ANON_KEY`: Public anon key
   - `SUPABASE_SERVICE_ROLE_KEY`: Service role key (keep server-side only!)

3. **Create a storage bucket:**
   - Go to Storage → New Bucket
   - Name: `audio-recordings` (or your `SUPABASE_BUCKET_NAME`)
   - Set appropriate RLS policies

4. **Set environment variables:**
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   SUPABASE_BUCKET_NAME=audio-recordings
   ```

---

## Deployment Options

### Render

1. **Create a new Web Service** connected to your GitHub repo

2. **Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```

3. **Start Command:**
   ```bash
   gunicorn slaq_project.wsgi:application --workers 3 --bind 0.0.0.0:$PORT
   ```

4. **Add a Background Worker** for Celery:
   ```bash
   celery -A slaq_project worker --loglevel=info
   ```

5. **Environment Variables:**
   - Add all variables from `.env.example.template`
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=False`
   - Use Render's managed PostgreSQL and Redis

6. **Render PostgreSQL:**
   - Create a PostgreSQL database in Render
   - Copy the Internal Database URL to `DATABASE_URL`

7. **Redis (for Celery):**
   - Use Render's Redis or an external provider (Upstash, Redis Cloud)
   - Set `CELERY_BROKER_URL`

### Railway

1. **Deploy from GitHub**

2. **Add PostgreSQL and Redis plugins**

3. **Set environment variables** in the Railway dashboard

4. **Start command:**
   ```bash
   gunicorn slaq_project.wsgi:application --workers 3
   ```

5. **Add a separate service for Celery worker**

### AWS (ECS/Fargate)

1. **Create ECR repository** and push Docker image

2. **Create ECS Cluster** with Fargate

3. **Create Task Definitions:**
   - Web: runs Gunicorn
   - Worker: runs Celery

4. **Use AWS Secrets Manager** for secrets

5. **Use RDS PostgreSQL** and **ElastiCache Redis**

### Docker

1. **Build the image:**
   ```bash
   docker build -t slaq-app .
   ```

2. **Run with docker-compose:**
   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       command: gunicorn slaq_project.wsgi:application --bind 0.0.0.0:8000
       ports:
         - "8000:8000"
       env_file:
         - .env
       depends_on:
         - db
         - redis

     worker:
       build: .
       command: celery -A slaq_project worker --loglevel=info
       env_file:
         - .env
       depends_on:
         - db
         - redis

     db:
       image: postgres:15
       environment:
         POSTGRES_DB: slaq_d_db
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: your_password
       volumes:
         - postgres_data:/var/lib/postgresql/data

     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"

   volumes:
     postgres_data:
   ```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check web service
curl https://your-domain.com/

# Check database connection
python manage.py check --database default

# Check Celery
celery -A slaq_project inspect ping
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

### 3. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 4. Test Supabase Connection

```python
from core.supabase_config import is_supabase_configured, get_supabase_client
print(f"Supabase configured: {is_supabase_configured()}")
client = get_supabase_client(use_service_role=True)
print(f"Client: {client}")
```

### 5. Monitor Logs

- Check application logs for errors
- Monitor Celery worker status
- Set up error tracking (Sentry recommended)

---

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('OK')"
```

### Static Files Not Loading

```bash
# Ensure collectstatic was run
python manage.py collectstatic --noinput

# Check STATIC_ROOT exists
ls -la staticfiles/
```

### Celery Tasks Not Running

```bash
# Check Redis connection
redis-cli ping

# Check Celery worker
celery -A slaq_project inspect active
```

### Supabase Upload Fails

1. Check bucket exists and has correct permissions
2. Verify `SUPABASE_SERVICE_ROLE_KEY` is set correctly
3. Check RLS policies allow uploads

### Audio Processing Fails

1. Ensure `ffmpeg` is installed: `ffmpeg -version`
2. Check file permissions in media directory
3. Verify audio file formats are supported

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY` (regenerated)
- [ ] `ALLOWED_HOSTS` contains only your domains
- [ ] HTTPS enabled (`SECURE_SSL_REDIRECT=True`)
- [ ] HSTS enabled
- [ ] Secure cookies enabled
- [ ] Database uses SSL connection
- [ ] Redis uses authentication
- [ ] Supabase service role key is server-side only
- [ ] All secrets in environment variables (not in code)
- [ ] `.env` files are in `.gitignore`
- [ ] Rotate any previously exposed keys

---

## Monitoring & Maintenance

### Recommended Tools

- **Error Tracking:** Sentry
- **Monitoring:** Prometheus + Grafana, or Datadog
- **Logging:** Structured logging to stdout (platform captures)
- **Backups:** Automated daily DB backups

### Regular Tasks

1. Monitor error rates
2. Check Celery queue depth
3. Review slow queries
4. Update dependencies for security patches
5. Rotate secrets periodically
