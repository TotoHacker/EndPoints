import os
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import xml.etree.ElementTree as ET
time=timeout=5
# Función para cargar y verificar URLs desde el XML
def load_services_from_xml():
    services = []
    # Construir la ruta absoluta del archivo XML
    xml_path = os.path.join(settings.BASE_DIR, 'monitor', 'templates', 'Prueba', 'DatosPrueba.xml')
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for item in root.findall('Registro'):
        url = item.find('UrlSite').text
        name = item.find('namesite').text
        services.append({'name': name, 'url': url})
    
    return services

# Función para verificar el estado de cada servicio
def check_service_status(service):
    try:
        response = requests.get(service['url'], time)
        status = 'live' if response.status_code == 200 else 'down'
        return {'name': service['name'], 'status': status, 'code': response.status_code}
    except (requests.exceptions.RequestException, ET.ParseError):
        return {'name': service['name'], 'status': 'down', 'code': 'N/A'}
#Funciones para verificar Apis
# def Check_Api_Status(service):
#     try:
#         response = requests.post(service)





# Vista principal para mostrar el estado de los servicios
def monitor_services(request):
    services = load_services_from_xml()
    status_list = [check_service_status(service) for service in services]
    return render(request, 'monitorApp/status_list.html', {'status_list': status_list})

# Otras vistas de ejemplo
def Login(request):
    return render(request, 'monitorApp/Login.html')

def Home(request):
    return render(request, 'monitorApp/Admin/Home.html')