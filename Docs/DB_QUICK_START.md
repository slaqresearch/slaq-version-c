# Quick Database Setup - SLAQ

## 🚀 Fastest Way (Automated Script)

```powershell
python setup_database.py
```

**What it does:**
- ✅ Tests PostgreSQL connection
- ✅ Creates `slaq_db` database
- ✅ Verifies everything works
- ✅ Updates your `.env` file (optional)

---

## 🎯 Manual Setup (GUI)

### Using pgAdmin 4:

1. **Open pgAdmin 4**
2. **Connect to PostgreSQL** (enter your password)
3. **Right-click "Databases"** → Create → Database
4. **Name:** `slaq_db`
5. **Click "Save"**

### Update `.env` file:
```env
DB_PASSWORD=your_postgres_password
```

---

## 💻 Manual Setup (Command Line)

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE slaq_db;

# Exit
\q
```

---

## ✅ After Database Created

```powershell
# 1. Run migrations
python manage.py migrate

# 2. Create admin user
python manage.py createsuperuser

# 3. Start server
python manage.py runserver
```

---

## ❌ Troubleshooting

### "Password authentication failed"
→ Update your `.env` file with the correct PostgreSQL password

### "PostgreSQL service not running"
```powershell
Get-Service -Name postgresql*
Start-Service postgresql-x64-13
```

### "psql not found"
→ Use full path: `"C:\Program Files\PostgreSQL\13\bin\psql"`

---

## 📖 Full Documentation

See `DATABASE_SETUP.md` for complete details and troubleshooting.

---

**Ready?** Run `python setup_database.py` to get started! 🎉
