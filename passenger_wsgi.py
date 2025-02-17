import os
import sys

# Establecer la ruta al directorio de tu aplicación
sys.path.append('/home/usuario/myapp') 
os.environ['DJANGO_SETTINGS_MODULE'] = 'MiddleTier.settings'  

# Importar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
