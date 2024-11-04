from django.urls import path
from django.contrib import admin
from monitor import views
from django.http import HttpResponseRedirect
from django.conf.urls.static import static

urlpatterns = [
    path('monitorApp/', views.monitor_services, name='monitor_services'),
    path('monitorApp/Login', views.Login, name='Login'),
    path('monitorApp/home', views.Home, name='home'),
    path('', lambda request: HttpResponseRedirect('/monitorApp/')),
]
