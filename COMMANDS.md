# 🔄 Django Migration Commands

## System Commands (Windows)

```bash
# Kill any running Python processes
taskkill /F /IM python.exe 2>nul; echo Killed any existing Python processes
```

---

## All Django Migration Commands

```bash
# Show all migrations
python manage.py showmigrations

# Create new migration after model changes
python manage.py makemigrations

# Apply pending migrations
python manage.py migrate

#clear the database and start fresh
python manage.py flush --no-input

# Apply migrations without prompts (non-interactive)
python manage.py migrate --noinput

# Migrate specific app
python manage.py migrate myapp

# Migrate specific app without prompts
python manage.py migrate myapp --noinput

# Rollback migration
python manage.py migrate myapp 0001

# Get SQL preview (don't execute)
python manage.py sqlmigrate myapp 0001

# Collect static files without prompts
python manage.py collectstatic --noinput

# Verbose migration output
python manage.py migrate --verbosity=2

```

