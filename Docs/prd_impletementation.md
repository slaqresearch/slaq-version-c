**Latest Updates — Production Deployment Review**

Date: 2025-12-06

Overview
- **Purpose:** Summarize the production-focused changes implemented to prepare this project for deployment, with emphasis on Supabase connectivity, environment configuration, database/Celery/Redis wiring, and security recommendations.
- **Scope:** Technical reviewer notes, sanitized environment examples, verification checklist, and next steps for safe production rollout.

Changes Implemented
- **Supabase integration:** Backend integration points were added so the application can read/write files to Supabase Storage and interact with Supabase services via server-side keys. The code references environment variables for `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` as the primary inputs.
- **Environment-driven configuration:** The project has been adapted to use environment variables for all runtime configuration (Python version pinning, environment mode, secret keys, allowed hosts, database connection, Supabase, and Celery/Redis broker). This centralization enables safer deployment to cloud hosts and platform services.
- **Database connectivity:** A full `DATABASE_URL` (Postgres) is accepted. The application supports using either a direct host/port DB configuration or a single `DATABASE_URL` for platforms like Render/Heroku.
- **Celery / Redis broker:** Celery broker URL has been updated to point at a managed Redis instance. The application reads `CELERY_BROKER_URL` from environment variables.

Sanitized Environment Example (do NOT commit secrets)
Use a secrets manager or platform environment variables. Below is a sanitized sample of the variables used; replace placeholders with your production secrets in the deployment platform (Render/AWS/GCP/Azure/etc.).

```
PYTHON_VERSION=3.10.0
ENVIRONMENT=production

DJANGO_SECRET_KEY=<REDACTED - store in secret manager>
DJANGO_ENCRYPT_KEY=<REDACTED - store in secret manager>

ALLOWED_HOSTS=*,localhost,127.0.0.1

# Database - prefer single DATABASE_URL for managed platforms
DATABASE_URL=postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:5432/<DB_NAME>

# Optional individual DB settings (if not using DATABASE_URL)
DB_NAME=<DB_NAME>
DB_USER=<DB_USER>
DB_USER_PASSWORD=<DB_PASSWORD>
DB_HOST=<DB_HOST>
DB_PORT=5432

# Supabase (keep service role key server-side only)
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_ANON_KEY=<anon-key - public but avoid embedding>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key - highly sensitive>
SUPABASE_BUCKET_NAME=<bucket-name>

# Celery / Redis broker
CELERY_BROKER_URL=redis://<user>:<password>@<redis-host>:<port>/0
```

Notes on the provided secrets
- If any real keys (example keys or secret values) were used during staging, rotate them now. Keys seen in development artifacts must be treated as compromised if they were committed anywhere public or shared. Replace them from your provider dashboard and update the production secret store.

Security & Hardening Recommendations
- **Never commit secrets to the repository.** Add a `.env` to `.gitignore` and use the host platform's secret manager or an external vault (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, etc.).
- **Use SUPABASE_SERVICE_ROLE_KEY only server-side.** The service role key bypasses Row-Level Security (RLS) and should never be exposed to browser or mobile clients.
- **Set `DEBUG=False` in production.** Verify that `ALLOWED_HOSTS` is configured tightly for production domains.
- **Secure cookies & TLS:** Configure `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, and enable HSTS (`SECURE_HSTS_SECONDS`).
- **Rotate keys** and set up automated rotation if supported by your provider.
- **Database credentials:** Use a managed Postgres instance with daily backups and point-in-time recovery where possible. Grant minimal privileges for the app user.
- **Rate-limit & CORS:** Apply appropriate CORS settings and rate limiting where external facing APIs exist.

Supabase specifics
- **Storage:** Use signed URLs for client downloads/uploads where applicable. Prefer server-generated signed URLs for uploads, and validate/scan any user-submitted files.
- **Auth & Policies:** Use RLS and policies for table-level protection. Use `SUPABASE_ANON_KEY` for client-side operations that require public access (with RLS) and `SUPABASE_SERVICE_ROLE_KEY` for server-only admin tasks.
- **Region & latency:** Ensure your Supabase project region aligns with your hosting region to reduce latency (e.g., Singapore region if your Render DB is in AP-Southeast).

Deployment Checklist (minimal, ordered)
- **1. Prepare secrets**: Add production secrets to your platform's secret store; do not commit them. Ensure `.gitignore` excludes any `.env` files.
- **2. Build & package**: Use `PYTHON_VERSION=3.10.0` compatible environment. Freeze dependencies in `requirements.txt` and install in a virtualenv/container.
- **3. DB migrations**: Run `python manage.py migrate` on the production database.
- **4. Static files**: Run `python manage.py collectstatic --noinput` and configure a static file host (CDN or object storage).
- **5. Celery workers**: Configure and start Celery workers pointing to `CELERY_BROKER_URL`. Ensure they are monitored and restart on failure.
- **6. Web server**: Serve the app using a WSGI server (Gunicorn) or ASGI server (Uvicorn/Daphne) behind a reverse proxy. Example Gunicorn command:

```
gunicorn slaq_project.wsgi:application --workers 3 --bind 0.0.0.0:$PORT
```

- **7. Health checks & smoke tests:** Validate endpoints, database connectivity, Supabase storage operations, Celery enqueue/worker processing, and background tasks.
- **8. Monitoring & logging:** Install monitoring (Prometheus/Datadog) and error tracking (Sentry). Log structured errors and background job traces.
- **9. Backups:** Ensure DB backups and Supabase storage snapshots are configured.
- **10. Rollback plan:** Prepare a deployment rollback strategy and snapshot DB prior to major migrations.

Verification & Testing
- Run an integration smoke test which:
  - queries the DB
  - enqueues a Celery task and verifies worker execution
  - uploads a small file to Supabase Storage and verifies retrieval via signed URL
  - tests user auth flows if applicable

Recommended Next Steps
- Move real secrets to the platform's secret manager and rotate any exposed keys immediately.
- Add CI/CD steps to automatically run migrations, collectstatic, run tests and then deploy.
- Add a short `DEPLOYMENT.md` that includes provider-specific commands (Render, AWS ECS, GKE, etc.) for reproducibility.

Files and locations referenced
- `core/supabase_config.py` — server-side Supabase initialization (reads `SUPABASE_*` env vars).
- `core/supabase_storage.py` — helpers for storage operations.
- `slaq_project/settings.py` — ensure production settings are applied from env and secure flags are set.

Closing
- The repository has been prepared to read all production configuration from environment variables and to connect to Supabase, Postgres and a managed Redis broker for Celery. Before going live, remove any sensitive values from the repository and rotate those credentials.

If you want, I can:
- commit this file and open a small PR, or
- add an automated `DEPLOYMENT.md` for a specific provider (Render/AWS/GCP), or
- run a local smoke test sequence (migrations, collectstatic, simple Supabase upload) — tell me which you'd like.