import os
import requests
from django.conf import settings
import xml.etree.ElementTree as ET
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from email.mime.image import MIMEImage


def Checktime(request):
    URL = "http://127.0.0.1:8000/api/Settings/"
    response = requests.get(URL)
    
    if response.status_code == 200:
        data = response.json()
        print('Respuesta de la API:', data)
        print('Tipo de respuesta:', type(data))  # Esto te dirá si es una lista o un diccionario
        
        if isinstance(data, list):
            # Si es una lista, puedes acceder a los elementos por su índice
            # Por ejemplo, accede al primer elemento de la lista
            data = data[0]  # Si solo necesitas el primer elemento de la lista
            print('Primer elemento de la lista:', data)
        
        horaInicioRevision = data['hour']
        minutoInicioRevision = data['minutes']
        vecesRevision = data['timesReview']
        print('Configuraciones: Hora de inicio:', horaInicioRevision, 'Minutos:', minutoInicioRevision, 'Veces de revisión:', vecesRevision)
    else:
        print('Error en la solicitud, detalles:', response.text)

    return {
        'horaInicioRevision': horaInicioRevision,
        'minutoInicioRevision': minutoInicioRevision,
        'vecesRevision': vecesRevision
    }

# horaInicioRevision = 11 
# minutoInicioRevision = 29 
# vecesRevision = 3  



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
    
