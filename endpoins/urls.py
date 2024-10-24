from django.urls import path
from django.contrib import admin
from monitor import views
from django.http import HttpResponseRedirect
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('monitorApp/', views.monitor_services, name='monitor_services'),
    path('', lambda request: HttpResponseRedirect('/monitorApp/')),  # Redirección
]
