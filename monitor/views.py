import os
import requests
from django.conf import settings
from django.shortcuts import render
import xml.etree.ElementTree as ET
import datetime
from django.http import JsonResponse

# Configuración de revisión (hora de inicio y número de veces de revisión al día)
horaInicioRevision = 1  # Hora en la que comienza la revisión, en formato de 24 horas (ej. 1 = 1 AM)
minutoInicioRevision = 18  # Minutos a los que comienza la revisión, ej. 20 = 20 minutos después de la hora
vecesRevision = 3  # Número de veces que se revisará en el día

# Función para convertir la hora con minutos decimales (ej. 1.14) a minutos
def hora_a_minutos(hora, minutos):
    return hora * 60 + minutos

# Función para calcular las próximas horas de revisión en función de los parámetros dados
def calcular_horas_revision(hora_inicio, minuto_inicio, veces):
    inicio_en_minutos = hora_a_minutos(hora_inicio, minuto_inicio)
    intervalo = 24 * 60 / veces  # Intervalo en minutos
    return [(inicio_en_minutos + i * intervalo) % (24 * 60) for i in range(veces)]

# Carga de servicios desde XML
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

    # Carga de sitios web
    for item in root.findall('Registro'):
        url = item.find('UrlSite')
        name = item.find('namesite')
        if url is not None and name is not None:
            websites.append({'name': name.text, 'url': url.text})

        # Carga de APIs
        api_url = item.find('UrlApi')
        api_name = item.find('nameApi')
        if api_url is not None and api_name is not None:
            method = item.find('Type').text if item.find('Type') is not None else 'HEAD'
            apis.append({'name': api_name.text, 'url': api_url.text, 'method': method})

    # Carga de servicios SOAP
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

# Función para verificar el estado de cada servicio usando una solicitud GET
def check_service_status(service):
    try:
        headers = {
            'Accept': '/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        response = requests.get(service['url'], headers=headers, timeout=5)

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

# Función para verificar el estado de un servicio SOAP
def check_soap_status(soap_service):
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        response = requests.post(soap_service['url'], data=soap_service['body'], headers=headers, timeout=5)
        status = 'Operativo' if response.status_code == 200 else 'Caído'
        return {'name': soap_service['name'], 'status': status, 'code': response.status_code}
    except requests.exceptions.RequestException as e:
        print(f"Error checking SOAP service {soap_service['name']}: {e}")
        return {'name': soap_service['name'], 'status': 'Caído', 'code': 'N/A'}

# Vista principal para el estado de los servicios, que revisa solo en las horas de revisión configuradas
def monitor_services(request):
    # Hora actual en minutos
    hora_actual = datetime.datetime.now()
    hora_actual_en_minutos = hora_a_minutos(hora_actual.hour, hora_actual.minute)
    
    # Calcular las horas de revisión en minutos
    horas_revision_en_minutos = calcular_horas_revision(horaInicioRevision, minutoInicioRevision, vecesRevision)

    # Revisar solo si estamos en la hora configurada
    if any(abs(hora_actual_en_minutos - revision) <= 5 for revision in horas_revision_en_minutos):  # Permitimos una pequeña tolerancia de 5 minutos
        websites, apis, soap_services = load_services_from_xml()
        website_status = [check_service_status(service) for service in websites]
        api_status = [check_service_status(api) for api in apis]
        soap_status = [check_soap_status(soap) for soap in soap_services]
    else:
        website_status = []
        api_status = []
        soap_status = []
        print("No es la hora de revisión, no se realizó ninguna revisión.")

    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
    })

# Otras vistas de ejemplo
def Login(request):
    return render(request, 'monitorApp/Login.html')

def Home(request):
    return render(request, 'monitorApp/Home.html')
