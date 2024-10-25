import os
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import xml.etree.ElementTree as ET

# Función para cargar y verificar URLs y APIs desde el XML
def load_services_from_xml():
    websites = []
    apis = []
    
    # Construir la ruta absoluta del archivo XML
    xml_path = os.path.join(settings.BASE_DIR, 'monitor', 'templates', 'Prueba', 'DatosPrueba.xml')
    
    # Verificar si el archivo existe
    if not os.path.isfile(xml_path):
        print(f"Error: El archivo XML no se encuentra en la ruta: {xml_path}")
        return websites, apis  # Devuelve listas vacías si no se encuentra el archivo
    
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Cargar servicios
    for item in root.findall('Registro'):
        url = item.find('UrlSite')
        name = item.find('namesite')
        if url is not None and name is not None:
            websites.append({'name': name.text, 'url': url.text})
        
        # Cargar APIs
        api_url = item.find('UrlApi')
        api_name = item.find('nameApi')
        if api_url is not None and api_name is not None:
            method = item.find('Type').text if item.find('Type') is not None else 'GET'
            apis.append({'name': api_name.text, 'url': api_url.text, 'method': method})

    return websites, apis

# Función para verificar el estado de cada servicio o API
def check_service_status(service):
    try:
        if 'method' in service:
            response = requests.request(service['method'].upper(), service['url'], timeout=5)
        else:
            response = requests.get(service['url'], timeout=5)
        
        status = 'Operativo' if response.status_code == 200 else 'Caído'
        return {'name': service['name'], 'status': status, 'code': response.status_code}
    except (requests.exceptions.RequestException, ET.ParseError):
        return {'name': service['name'], 'status': 'Caído', 'code': 'N/A'}

# Vista principal para mostrar el estado de los servicios
def monitor_services(request):
    websites, apis = load_services_from_xml()
    website_status = [check_service_status(service) for service in websites]
    api_status = [check_service_status(api) for api in apis]
    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
    })

# Otras vistas de ejemplo
def Login(request):
    return render(request, 'monitorApp/Login.html')

def Home(request):
    return render(request, 'monitorApp/Admin/Home.html')