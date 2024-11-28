from django.contrib import admin
from .models import SettingsMonitor
from . models import SysError

admin.site.site_header='Prueba1'
admin.site.register(SysError)
admin.site.register(SettingsMonitor)

