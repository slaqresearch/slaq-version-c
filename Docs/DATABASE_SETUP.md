# PostgreSQL Database Setup for SLAQ

Complete guide to set up PostgreSQL database for the SLAQ project on Windows.

---

## Prerequisites

- PostgreSQL installed on your system
- pgAdmin 4 (comes with PostgreSQL installation)
- OR psql command-line tool

---

## Method 1: Using pgAdmin 4 (GUI - Easiest)

### Step 1: Open pgAdmin 4

1. Search for "pgAdmin 4" in Windows Start menu
2. Open the application
3. Enter your master password if prompted

### Step 2: Connect to PostgreSQL Server

1. In the left sidebar, expand "Servers"
2. Click on "PostgreSQL 13" (or your version)
3. Enter your PostgreSQL password when prompted
   - This is the password you set during PostgreSQL installation

### Step 3: Create Database

1. Right-click on "Databases"
2. Select **"Create" → "Database..."**
3. In the dialog:
   - **Database name:** `slaq_db`
   - **Owner:** `postgres` (default)
   - Click **"Save"**

### Step 4: Verify Database Created

- You should see `slaq_db` appear in the databases list
- ✅ Database is ready!

### Step 5: Update Your `.env` File

```env
DB_NAME=slaq_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
DB_HOST=localhost
DB_PORT=5432
```

**Important:** Replace `your_postgres_password_here` with the actual password you use to log into pgAdmin!

---

## Method 2: Using psql Command Line

### Step 1: Open Command Prompt or PowerShell

```powershell
# Navigate to PostgreSQL bin directory (adjust path for your installation)
cd "C:\Program Files\PostgreSQL\13\bin"
```

### Step 2: Connect to PostgreSQL

```powershell
# Connect as postgres user
.\psql -U postgres

# Enter your PostgreSQL password when prompted
```

### Step 3: Create Database

```sql
-- Create the database
CREATE DATABASE slaq_db;

-- Verify it was created
\l

-- Connect to the database (optional, to verify)
\c slaq_db

-- Exit psql
\q
```

### Step 4: Update Your `.env` File

```env
DB_NAME=slaq_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
DB_HOST=localhost
DB_PORT=5432
```

---

## Method 3: Using SQL Script (Provided)

### Step 1: Use the Provided Script

The project includes `setup_database.sql`. You can run it:

**Via psql:**
```powershell
cd "C:\Program Files\PostgreSQL\13\bin"
.\psql -U postgres -f "C:\Users\Faheem\Desktop\AI\Slaq\slaq_project\setup_database.sql"
```

**Via pgAdmin:**
1. Open pgAdmin
2. Click on your PostgreSQL server
3. Click "Tools" → "Query Tool"
4. Open `setup_database.sql` file
5. Click "Execute" (▶️ button)

---

## Method 4: Create Database with Python Script (Automated)

I've created a Python script to automate this:

```powershell
# Run from your project directory
python setup_database.py
```

This script will:
- Prompt for your PostgreSQL password
- Create the database
- Verify connection
- Update your `.env` file (optional)

---

## Common Issues & Solutions

### Issue 1: "psql: command not found" or "psql is not recognized"

**Solution:** Add PostgreSQL to your PATH or use full path:
```powershell
cd "C:\Program Files\PostgreSQL\13\bin"
.\psql -U postgres
```

### Issue 2: "password authentication failed for user postgres"

**Solutions:**
1. **Check your password:** Make sure you're using the correct PostgreSQL password
2. **Reset password:**
   ```powershell
   # In psql as superuser
   ALTER USER postgres WITH PASSWORD 'new_password';
   ```
3. **Check pg_hba.conf:** Ensure `localhost` connections are allowed

### Issue 3: "database slaq_db already exists"

**Solution:** Database is already created! Just verify your `.env` file has the correct password.

### Issue 4: "connection refused on port 5432"

**Solutions:**
1. **Check if PostgreSQL is running:**
   ```powershell
   # Check service status
   Get-Service -Name postgresql*
   
   # Start if not running
   Start-Service postgresql-x64-13  # Adjust version number
   ```
2. **Verify port in postgresql.conf:**
   - Default location: `C:\Program Files\PostgreSQL\13\data\postgresql.conf`
   - Check `port = 5432`

### Issue 5: "role 'postgres' does not exist"

**Solution:** Create the postgres user:
```sql
CREATE USER postgres WITH SUPERUSER PASSWORD 'your_password';
```

---

## Verify Database Setup

After creating the database, test the connection:

### Option A: Using Python

```python
# test_db_connection.py
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    print("✅ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Option B: Using Django

```powershell
# Test Django database connection
python manage.py check --database default
```

---

## Next Steps After Database Creation

### 1. Update `.env` File

Make sure your `.env` file has the correct password:

```env
# Database Configuration
DB_NAME=slaq_db
DB_USER=postgres
DB_PASSWORD=YOUR_ACTUAL_PASSWORD_HERE
DB_HOST=localhost
DB_PORT=5432
```

### 2. Run Migrations

```powershell
# Apply database migrations
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, diagnosis, django_celery_results, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  ...
  ✅ All migrations applied successfully!
```

### 3. Create Superuser

```powershell
# Create admin account
python manage.py createsuperuser
```

Follow prompts:
- Username: (your choice, e.g., `admin`)
- Email: (your email)
- Password: (choose a secure password)

### 4. Test the Server

```powershell
# Start development server
python manage.py runserver
```

Visit: `http://localhost:8000`

---

## Database Information

### Database Structure (After Migration)

Tables created:
- `auth_*` - Django authentication tables
- `core_patient` - Patient profiles
- `diagnosis_audiorecording` - Audio recordings
- `diagnosis_analysisresult` - Analysis results
- `django_celery_results_*` - Celery task results
- `django_session` - User sessions
- And more Django system tables

### Database Size

- **Initial (empty):** ~10 MB
- **With data:** Grows with audio files and analyses
- **Recommended:** Monitor size as you add recordings

---

## PostgreSQL Useful Commands

```sql
-- List all databases
\l

-- Connect to database
\c slaq_db

-- List all tables
\dt

-- View table structure
\d core_patient

-- Count records
SELECT COUNT(*) FROM core_patient;

-- Exit psql
\q
```

---

## Backup & Restore (Bonus)

### Backup Database

```powershell
cd "C:\Program Files\PostgreSQL\13\bin"
.\pg_dump -U postgres -d slaq_db -f "C:\backup\slaq_db_backup.sql"
```

### Restore Database

```powershell
cd "C:\Program Files\PostgreSQL\13\bin"
.\psql -U postgres -d slaq_db -f "C:\backup\slaq_db_backup.sql"
```

---

## Alternative: Use SQLite for Development (Optional)

If PostgreSQL is giving you trouble, you can temporarily use SQLite:

**In `settings.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Note:** Switch back to PostgreSQL for production!

---

## Security Best Practices

1. ✅ **Never commit `.env` file** (already in `.gitignore`)
2. ✅ **Use strong passwords** for PostgreSQL
3. ✅ **Change default passwords** in production
4. ✅ **Restrict database access** to localhost in development
5. ✅ **Use environment variables** for credentials (already configured)

---

## Quick Reference

```powershell
# Check PostgreSQL service
Get-Service -Name postgresql*

# Start PostgreSQL
Start-Service postgresql-x64-13

# Stop PostgreSQL
Stop-Service postgresql-x64-13

# Connect to database
psql -U postgres -d slaq_db

# Run Django migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## Need Help?

Common PostgreSQL locations on Windows:
- **Installation:** `C:\Program Files\PostgreSQL\13\`
- **Data Directory:** `C:\Program Files\PostgreSQL\13\data\`
- **Config File:** `C:\Program Files\PostgreSQL\13\data\postgresql.conf`
- **Binaries:** `C:\Program Files\PostgreSQL\13\bin\`

---

**Ready to proceed?** Once database is created, run migrations and start developing! 🚀
