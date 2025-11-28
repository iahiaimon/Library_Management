import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phase_1.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Drop and recreate all tables
print("🗑️  Deleting all tables from demo_db...")

# Get list of all tables
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='demo_db'")
tables = cursor.fetchall()

if tables:
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    
    # Drop all tables
    for table in tables:
        table_name = table[0]
        print(f"   Dropping table: {table_name}")
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    print("✅ All tables deleted successfully!")
else:
    print("ℹ️  No tables found to delete")

cursor.close()
