from django.shortcuts import render
from .models import MonitoredService

def monitor_services(request):
    services = MonitoredService.objects.all()
    return render(request, 'monitorApp/status_list.html', {'services': services})
