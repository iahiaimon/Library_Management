import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Root App.settings')
django.setup()

from django.db import connections
from django.db.models import Count
from accounts.models import Student, UserApproval
from django.contrib.auth.models import User

print("=" * 60)
print("DATABASE CONNECTION INFO")
print("=" * 60)

# Show which database is configured
from django.conf import settings
print(f"\nConfigured Database: {settings.DATABASES['default']}")

# Show actual connection being used
default_conn = connections['default']
print(f"\nActual Connection Engine: {default_conn.settings_dict['ENGINE']}")
print(f"Actual Database Name: {default_conn.settings_dict['NAME']}")

print("\n" + "=" * 60)
print("DATA IN CURRENT DATABASE")
print("=" * 60)

users_count = User.objects.count()
students_count = Student.objects.count()
approvals_count = UserApproval.objects.count()

print(f"\nUsers in auth_user: {users_count}")
print(f"Students in myapp_student: {students_count}")
print(f"Approvals in myapp_userapproval: {approvals_count}")

if users_count > 0:
    print("\nUsers found:")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email})")

if approvals_count > 0:
    print("\nApprovals found:")
    for approval in UserApproval.objects.all():
        print(f"  - {approval.user.username} ({approval.role})")
else:
    print("\n⚠️  NO DATA FOUND IN DATABASE!")
