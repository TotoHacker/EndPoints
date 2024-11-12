from django.urls import path, include
from django.contrib import admin
from monitor import views
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
urlpatterns = [
    #Api
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    #Others Views
    path('monitorApp/', views.monitor_services, name='monitor_services'),
    path('monitorApp/Login', views.Login, name='Login'),
    #solo si el usuario esta logeado puede ver
    path('monitorApp/home', views.Home, name='home'),
    path('', lambda request: HttpResponseRedirect('/monitorApp/')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
