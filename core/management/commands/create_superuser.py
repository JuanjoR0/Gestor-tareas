
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Crea un superusuario si no existe'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'Juanjo')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'juanjorodriguez682@gmail.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'usuario1234')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Superusuario creado'))
        else:
            self.stdout.write('Superusuario ya existe')
