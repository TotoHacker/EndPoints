from django.contrib import admin
from .models import SettingsMonitor
from . models import SysError

admin.site.site_header='EndPoints Dolphin Discovery'
admin.site.register(SysError)
admin.site.register(SettingsMonitor)

