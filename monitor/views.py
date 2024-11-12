import os
import requests
from django.conf import settings
from django.shortcuts import render
import xml.etree.ElementTree as ET
import datetime
from django.http import JsonResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from email.mime.image import MIMEImage
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Configuración de revisión (hora de inicio y número de veces de revisión al día)
horaInicioRevision = 11  # Hora en la que comienza la revisión, en formato de 24 horas (ej. 1 = 1 AM)
minutoInicioRevision = 54 # Minutos a los que comienza la revisión, ej. 20 = 20 minutos después de la hora
vecesRevision = 3  # Número de veces que se revisará en el día


# Vista para el inicio de sesión

def send_email(subject, body, to_email):
    try:
        # Configuración del servidor SMTP de Gmail
        from_email = settings.EMAIL_HOST_USER  # Asegúrate de que esté configurado en settings.py
        password = settings.EMAIL_HOST_PASSWORD

        # Crear el mensaje de correo
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Crear el cuerpo del correo en formato HTML
        html_body = f"""
        <html>
        <head></head>
        <body>
            <p>Buen día Ingeniero Antonio,</p>
            <p>El día de hoy los servicios que se cayeron son:</p>
            <ul>
        """

        # Agregar los sitios caídos al cuerpo del correo
        for site in body:
            html_body += f"<li><strong>{site['name']}</strong>: {site['url']}</li>"

        html_body += """
            </ul>
            <p>Saludos cordiales,</p>
            <p>El equipo de monitoreo</p>
            <img src="cid:logo" alt="Logo" width="full" height="full">
        </body>
        </html>
        """

        # Adjuntar el cuerpo HTML
        msg.attach(MIMEText(html_body, 'html'))

        # Incluir la imagen como adjunto y referenciarla en el HTML
        with open(os.path.join(settings.BASE_DIR, 'static', 'imagenes', 'LogoFondo.jpeg'), 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<logo>')
            msg.attach(img)

        # Conectar con el servidor SMTP de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  
        server.login(from_email, password)

        # Enviar el correo
        server.sendmail(from_email, to_email, msg.as_string())

        # Cerrar la conexión
        server.quit()
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
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

    xml_path = os.path.join(settings.BASE_DIR, 'Server', 'Prueba', 'DatosPrueba.xml')

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
            'url': service['url'],
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
    hora_actual = datetime.datetime.now()
    hora_actual_en_minutos = hora_a_minutos(hora_actual.hour, hora_actual.minute)
    horas_revision_en_minutos = calcular_horas_revision(horaInicioRevision, minutoInicioRevision, vecesRevision)

    website_status = []
    api_status = []
    soap_status = []

    # Compara si la hora actual está en las horas de revisión programadas
    if hora_actual_en_minutos in horas_revision_en_minutos:
        websites, apis, soap_services = load_services_from_xml()

        website_status = [check_service_status(service) for service in websites]
        api_status = [check_service_status(api) for api in apis]
        soap_status = [check_soap_status(soap) for soap in soap_services]
        # print(website_status)


        # Filtrar los servicios caídos y asegurarse de incluir la URL
        sitios_caidos = [
            {
                'name': service['name'], 
                'code':service['code'],
                'url': service['url'] if 'url' in service and service['url'] else 'URL no disponible'
            }
            for service in website_status 
            if service['status'] != 'Operativo'
        ]

        if sitios_caidos:
            # Crear el cuerpo del correo
            subject = "Servicios caídos en el monitor"
            # Enviar el correo con los servicios caídos
            send_email(subject, sitios_caidos, 'anovelo@thedolphinco.com')
            # send_email(subject, sitios_caidos, 'totochucl@gmail.com')

            for sitio in sitios_caidos:
                URL="http://127.0.0.1:8000/api/syserrors/"
                DATA = {
                    "site_url": sitio['url'], 
                    "error_site_code": sitio['code'],  # Ajusta los campos según corresponda
                    "date_error": datetime.datetime.now().strftime("%Y-%m-%d")

                }

                response = requests.post(URL, json=DATA)

                if response.status_code == 200:
                    print('Solicitud exitosa')
                    print('Data:', response.json())
                else:
                    print('Error en la solicitud, detalles:', response.text)  
    else:
        print("No es la hora de revisión, no se realizó ninguna revisión.")
        print("Horas de revisión generadas:", horas_revision_en_minutos)

    
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

def CrudU(request):
    return render(request,'monitorApp/Admin/Crud.html')
 