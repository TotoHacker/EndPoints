import requests
from django.http import JsonResponse
from django.shortcuts import render
from .models import MonitoredService
import xml.etree.cElementTree as ET
# import of xml
from xml.etree.ElementTree import parse
documents = parse('./templates/Prueba/DatosPrueba.xml')
for item in documents.iterfind('record'):
    print(item.findtext('UrlSite'))

#Others Funtions
def monitor_services(request):
    services = MonitoredService.objects.all()
    return render(request, 'monitorApp/status_list.html', {'services': services})

def Login(request):
    services = MonitoredService.objects.all()
    return render(request, 'monitorApp/Login.html', {'services': services})
def Home(request):
    services = MonitoredService.objects.all()
    return render(request, 'monitorApp/Admin/Home.html', {'services': services})

def check_service_status(service):
    try:
        response = requests.get(service.url, timeout=5)
        if service.response_format == 'JSON':
            response.json()  # error if not valid JSON
        elif service.response_format == 'XML':
            ET.fromstring(response.content)  # error if not valid XML
        return {'name': service.name, 'status': 'live', 'code': response.status_code}
    except (requests.exceptions.RequestException, ET.ParseError, ValueError):
        return {'name': service.name, 'status': 'down'}