import os
import requests
from django.conf import settings
from django.shortcuts import render
import xml.etree.ElementTree as ET
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.http import JsonResponse



# Function to load URLs, APIs, and SOAP services from the XML
def load_services_from_xml():
    websites = []
    apis = []
    soap_services = []

    xml_path = os.path.join(settings.BASE_DIR, 'Server', 'Prueba', 'DatosPrueba.xml')

    if not os.path.isfile(xml_path):
        print(f"Error: El archivo XML no se encuentra en la ruta: {xml_path}")
        return websites, apis, soap_services

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Load websites
    for item in root.findall('Registro'):
        url = item.find('UrlSite')
        name = item.find('namesite')
        if url is not None and name is not None:
            websites.append({'name': name.text, 'url': url.text})

        # Load APIs
        api_url = item.find('UrlApi')
        api_name = item.find('nameApi')
        if api_url is not None and api_name is not None:
            method = item.find('Type').text if item.find('Type') is not None else 'HEAD'
            apis.append({'name': api_name.text, 'url': api_url.text, 'method': method})

    # Load SOAP services for both servers
    for server_number in range(1, 3):
        soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <obtenerEstadodeLaConexion xmlns="http://dtraveller.com/">
              <server>{server_number}</server>
            </obtenerEstadodeLaConexion>
          </soap:Body>
        </soap:Envelope>"""
        server_name = f'Servidor {"Mexico" if server_number == 1 else "Caribe"} {server_number}'

        soap_services.append({
            'name': server_name,
            'url': 'https://dtnsr-ws.dtraveller.com/dtraveller.asmx?op=obtenerEstadodeLaConexion',
            'body': soap_request
        })

    return websites, apis, soap_services

# Function to check the status of each website or API using a HEAD request
# def check_service_status(service):
    try:
        headers = {
            'Accept': '/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        
        # Usamos GET en lugar de HEAD
        response = requests.get(service['url'], headers=headers, timeout=5)

        #Lo que trae el sitio xd
        # print(f"URL: {service['url']}")
        # print(f"Status Code: {response.status_code}")
        # print(f"Headers: {response.headers}")
        # print(f"Content: {response.text[:500]}")  

        # Verificamos el estado de la respuesta
        if response.status_code == 200:
            status = 'Operativo'
        elif response.status_code == 406:
            status = 'Error 406: Not Acceptable'
        else:
            status = 'Caído'

        return {
            'name': service['name'],
            'status': status,
            'code': response.status_code,
            'response': response.text[:500]
        }
    except requests.exceptions.RequestException as e:
        print(f"Error checking service {service['name']}: {e}")
        return {
            'name': service['name'],
            'status': 'Caído',
            'code': 'N/A'
        }
def check_soap_status(soap_service):
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        response = requests.post(soap_service['url'], data=soap_service['body'], headers=headers, timeout=5)
        status = 'Operativo' if response.status_code == 200 else 'Caído'
        return {'name': soap_service['name'], 'status': status, 'code': response.status_code}
    except requests.exceptions.RequestException as e:
        print(f"Error checking SOAP service {soap_service['name']}: {e}")
        return {'name': soap_service['name'], 'status': 'Caído', 'code': 'N/A'}

# View to display the services status
def services_status_view(request):
    websites, apis, soap_services = load_services_from_xml()

    # Check status of each service
    # website_status = [check_service_status(service) for service in websites]
    # api_status = [check_service_status(service) for service in apis]
    soap_status = [check_soap_status(service) for service in soap_services]

    return render(request, 'monitorApp/status_list.html', {
        # 'website_status': website_status,
        # 'api_status': api_status,
        'soap_status': soap_status,
    })

# Main view to display the status of services
def monitor_services(request):
    websites, apis, soap_services = load_services_from_xml()
    # website_status = [check_service_status(service) for service in websites]
    # api_status = [check_service_status(api) for api in apis]
    soap_status = [check_soap_status(soap) for soap in soap_services]

    return render(request, 'monitorApp/status_list.html', {
        # 'website_status': website_status,
        # 'api_status': api_status,
        'soap_status': soap_status,
    })

# Other example views
def Login(request):
    return render(request, 'monitorApp/Login.html')

def Home(request):
    return render(request, 'monitorApp/Home.html')
