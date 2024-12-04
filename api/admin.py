from django.contrib import admin
from .models import SettingsMonitor
from . models import SysError
from . models import LastCheckStatus

admin.site.site_header='EndPoints Dolphin Discovery'
admin.site.register(SysError)
admin.site.register(SettingsMonitor)
admin.site.register(LastCheckStatus)
