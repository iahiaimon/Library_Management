# import os
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Root App.settings')
# django.setup()

# from django.contrib.auth.models import User

# # Create superuser
# admin, created = User.objects.get_or_create(
#     username='admin',
#     defaults={
#         'email': 'admin@demo.com',
#         'is_staff': True,
#         'is_superuser': True,
#     }
# )

# admin.set_password('admin123')
# admin.save()

# print(f"✅ Superuser created/updated:")
# print(f"   Username: admin")
# print(f"   Email: admin@demo.com")
# print(f"   Password: admin123")
# print(f"   Created: {created}")
