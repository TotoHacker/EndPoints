import os
import requests
from django.conf import settings
from django.shortcuts import render
import xml.etree.ElementTree as ET

# Función para cargar URLs, APIs y SOAP desde el XML
def load_services_from_xml():
    websites = []
    apis = []
    soap_services = []
    
    xml_path = os.path.join(settings.BASE_DIR, 'monitor', 'templates', 'Prueba', 'DatosPrueba.xml')
    
    if not os.path.isfile(xml_path):
        print(f"Error: El archivo XML no se encuentra en la ruta: {xml_path}")
        return websites, apis, soap_services
    
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Cargar servicios y APIs
    for item in root.findall('Registro'):
        url = item.find('UrlSite')
        name = item.find('namesite')
        if url is not None and name is not None:
            websites.append({'name': name.text, 'url': url.text})
        
        api_url = item.find('UrlApi')
        api_name = item.find('nameApi')
        if api_url is not None and api_name is not None:
            method = item.find('Type').text if item.find('Type') is not None else 'GET'
            apis.append({'name': api_name.text, 'url': api_url.text, 'method': method})

    # Cargar servicios SOAP
    soap_request = root.find('SOAP/Request/RequestBody')
    if soap_request is not None:
        soap_services.append({
            'name': 'Ejemplo de API SOAP',
            'url': 'http://ebgral.dtraveller.com/v2.1/tours',  # Cambia esto si necesitas una URL específica para el SOAP
            'body': soap_request.text.strip()
        })

    return websites, apis, soap_services

# Función para verificar el estado de cada servicio o API
def check_service_status(service):
    try:
        if 'method' in service:
            response = requests.request(service['method'].upper(), service['url'], timeout=5)
        else:
            response = requests.get(service['url'], timeout=5)
        
        status = 'Operativo' if response.status_code == 200 else 'Caído'
        return {'name': service['name'], 'status': status, 'code': response.status_code}
    except requests.exceptions.RequestException:
        return {'name': service['name'], 'status': 'Caído', 'code': 'N/A'}

# Nueva función para verificar el estado de un servicio SOAP
def check_soap_status(soap_service):
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        response = requests.post(soap_service['url'], data=soap_service['body'], headers=headers, timeout=5)
        
        # Aquí puedes verificar la respuesta SOAP en lugar del código de estado
        status = 'Operativo' if response.status_code == 200 and "<GetTourResponse" in response.text else 'Caído'
        return {'name': soap_service['name'], 'status': status, 'code': response.status_code}
    except requests.exceptions.RequestException:
        return {'name': soap_service['name'], 'status': 'Caído', 'code': 'N/A'}

# Vista principal para mostrar el estado de los servicios
def monitor_services(request):
    websites, apis, soap_services = load_services_from_xml()
    website_status = [check_service_status(service) for service in websites]
    api_status = [check_service_status(api) for api in apis]
    soap_status = [check_soap_status(soap) for soap in soap_services]
    
    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
    })


# Otras vistas de ejemplo
def Login(request):
    return render(request, 'monitorApp/Login.html')

def Home(request):
    return render(request, 'monitorApp/Admin/Home.html')
