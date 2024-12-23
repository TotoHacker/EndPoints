from django.urls import path, include
from django.contrib import admin
from MiddleTier import views
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación
    path('Login', views.Login, name='Login'),
    path('logout', views.logout_view, name='logout'),

    # API
    path('api/', include('api.urls')),

    # Monitor (requiere autenticación)
    path('monitorApp/', login_required(views.monitor_services), name='monitor_services'),
    path('Home', login_required(views.Home), name='home'),
    path('SettingsMonitor', login_required(views.SettingsMonitor), name='Settings'),
    path('monitorApp/check-now', login_required(views.check_now), name='check_now'),
    path('Inicio', views.pagetext, name='Inicio'),
    # Redirección principal al Login
    path('', lambda request: HttpResponseRedirect('/Login')),
]

# Configuración para servir archivos estáticos en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
