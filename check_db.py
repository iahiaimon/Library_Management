import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Root App.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print("Tables in demo_db:")
for table in tables:
    print(f"  - {table[0]}")

# Check if data exists in Student table
cursor.execute("SELECT COUNT(*) FROM myapp_student")
count = cursor.fetchone()[0]
print(f"\nRecords in myapp_student: {count}")

# Check if data exists in User table
cursor.execute("SELECT COUNT(*) FROM auth_user")
count = cursor.fetchone()[0]
print(f"Records in auth_user: {count}")

# List all users
cursor.execute("SELECT id, username, email FROM auth_user")
users = cursor.fetchall()
print("\nUsers in auth_user:")
for user in users:
    print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")

cursor.close()
