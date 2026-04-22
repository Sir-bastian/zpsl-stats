import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zpsl.settings')
django.setup()

User = get_user_model()
if not User.objects.filter(username='sirbastian').exists():
    User.objects.create_superuser('sirbastian', 'madziwanzirasebastiantwo@gmail.com', 'zpslstats')
    print("Superuser created!")
else:
    print("Superuser already exists.")
