import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapsearch.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='Tareq')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f'✅ Success! User "{user.username}" is now a superuser.')
    print(f'   - is_staff: {user.is_staff}')
    print(f'   - is_superuser: {user.is_superuser}')
    print(f'   - is_active: {user.is_active}')
except User.DoesNotExist:
    print('❌ User "Tareq" not found!')
    print('Creating new superuser "Tareq"...')
    user = User.objects.create_superuser(
        username='Tareq',
        email='tareq@accessadvisr.com',
        password='admin123'
    )
    print(f'✅ Superuser "Tareq" created successfully!')
