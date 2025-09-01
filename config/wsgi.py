# config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

# --- Inicializar datos si la BD está vacía ---
try:
    from core.init_db import initialize_data
    initialize_data()
except Exception as e:
    print("⚠️ Error inicializando datos:", e)
