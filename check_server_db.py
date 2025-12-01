import os
import django
import sys

# Make sure we're using the correct settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Root App.settings')

# Reset Django to force fresh import
if 'django.db.connections' in sys.modules:
    del sys.modules['django.db.connections']

django.setup()

from django.db import connection, connections
from django.contrib.auth.models import User

print("=" * 70)
print("DJANGO SERVER DATABASE CHECK")
print("=" * 70)

# Get the active database connection
db_name = connection.settings_dict['NAME']
db_engine = connection.settings_dict['ENGINE']
print(f"\n📊 Connected Database: {db_name}")
print(f"🔧 Database Engine: {db_engine}")

# Try to query users
try:
    from django.db import connection
    from django.db.utils import OperationalError
    
    # Force a database query
    cursor = connection.cursor()
    cursor.execute("SELECT DATABASE()")
    current_db = cursor.fetchone()[0]
    print(f"✅ Currently using database: {current_db}")
    
    # Check user count
    users = User.objects.all().count()
    print(f"👤 Users in database: {users}")
    
    if users > 0:
        print("\n⚠️  USERS FOUND IN DATABASE (OLD DATA):")
        for user in User.objects.all()[:5]:
            print(f"   - {user.username} (email: {user.email})")
    else:
        print("\n✅ DATABASE IS EMPTY (CORRECT!)")
        
except Exception as e:
    print(f"❌ Error: {e}")
