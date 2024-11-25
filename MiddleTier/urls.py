from django.urls import path, include
from django.contrib import admin
from MiddleTier import views
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    #login
    path('Login', views.Login, name='Login'),
    #Api
    path('api/', include('api.urls')),
    #solo si el usuario esta logeado puede ver
    path('monitorApp/', login_required(views.monitor_services), name='monitor_services'),
    path('Home', login_required(views.Home), name='home'),
    path('CrudErrors', login_required(views.CrudE), name='CrudErrors'),
    path('CrudUser', login_required(views.CrudU), name='Crud'),
    path("SettingMonitor", login_required(views.SettingsMonitor), name="Settings"),

    #vista principal
    path('', lambda request: HttpResponseRedirect('/Login')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
