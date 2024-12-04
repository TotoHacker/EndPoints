import requests
from django.shortcuts import render, redirect
from monitor.views import (
    load_services_from_xml, check_service_status,
    check_soap_status, send_email
)
from datetime import datetime, timedelta
from django.contrib.auth import logout


def Checktime():
    URL = "http://127.0.0.1:8000/api/Settings/"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        print('Respuesta de la API:', data)

        if isinstance(data, list):
            data = data[0]  # Si es una lista, toma el primer elemento

        interval_hours = data['interval_hours']
        interval_minutes = data['interval_minutes']
        start_datetime = datetime.fromisoformat(data['start_datetime'])  # Hora inicial como datetime

        print('Configuraciones: Hora de inicio:', start_datetime,
              'Intervalo (horas):', interval_hours,
              'Intervalo (minutos):', interval_minutes)
    else:
        print('Error en la solicitud, detalles:', response.text)
        return None

    return {
        'interval_hours': interval_hours,
        'interval_minutes': interval_minutes,
        'start_datetime': start_datetime
    }


def calcular_proximas_revisiones(start_datetime, interval_hours, interval_minutes, cantidad_revisiones):
    resultados = []
    intervalo = timedelta(hours=interval_hours, minutes=interval_minutes)
    proxima_revision = start_datetime

    for _ in range(cantidad_revisiones):
        resultados.append(proxima_revision)
        proxima_revision += intervalo

    return resultados


def realizar_revision():
    websites, apis, soap_services = load_services_from_xml()

    # Comprobar estados
    website_status = [check_service_status(service) for service in websites]
    api_status = [check_service_status(api) for api in apis]
    soap_status = [check_soap_status(soap) for soap in soap_services]

    # Identificar sitios caídos
    sitios_caidos = [
        {
            'name': service['name'],
            'code': service['code'],
            'url': service.get('url', 'URL no disponible')
        }
        for service in website_status if service['status'] != 'Operativo'
    ]

    # Enviar notificaciones si hay sitios caídos
    if sitios_caidos:
        subject = "Servicios caídos en el monitor"
        send_email(subject, sitios_caidos, 'totochucl@gmail.com')

        # Registrar errores en la API
        for sitio in sitios_caidos:
            URL = "http://127.0.0.1:8000/api/syserrors/"
            DATA = {
                "site_url": sitio['url'],
                "error_site_code": sitio['code'],
                "date_error": datetime.now().strftime("%Y-%m-%d"),
            }

            response = requests.post(URL, json=DATA)
            if response.status_code == 200:
                print('Registro de error exitoso para:', sitio['name'])
            else:
                print('Error registrando el sitio caído:', response.text)

    return website_status, api_status, soap_status
def savestates(service_status):
    url = 'http://127.0.0.1:8000/api/LastCheck/'
    for service in service_status:
        data = {
            "service_type": service['type'],
            "service_name": service['name'],
            "service_url": service['url'],
            "status": service['status'],
            "response_code": service['code'],
            "checked_at": datetime.now().isoformat()
        }
        response = requests.post(url, json=data)
        if response.status_code != 201:
            print('Error al guardar estado:', response.text)


# Función para recuperar los últimos estados desde la API
def seetates():
    URL = "http://127.0.0.1:8000/api/LastCheck/"
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    return []


def monitor_services(request):
    config = Checktime()
    if not config:
        print("Error al obtener configuraciones de Checktime.")
        return render(request, 'monitorApp/status_list.html', {
            'website_status': [],
            'api_status': [],
            'soap_status': [],
            'last_status': []
        })

    start_datetime = config['start_datetime']
    interval_hours = config['interval_hours']
    interval_minutes = config['interval_minutes']
    cantidad_revisiones = 24 * 60 // (interval_hours * 60 + interval_minutes)

    horas_revision = calcular_proximas_revisiones(start_datetime, interval_hours, interval_minutes, cantidad_revisiones)
    horas_revision_en_minutos = [hora.hour * 60 + hora.minute for hora in horas_revision]

    hora_actual = datetime.now()  # Hora del equipo directamente
    hora_actual_en_minutos = hora_actual.hour * 60 + hora_actual.minute

    website_status = []
    api_status = []
    soap_status = []

    last_status = seetates()  # Obtener los últimos estados de los servicios

    if hora_actual_en_minutos in horas_revision_en_minutos:
        print(f"Hora de revisión: {hora_actual.strftime('%Y-%m-%d %H:%M:%S')}")
        website_status, api_status, soap_status = realizar_revision()
    else:
        print(f"No es hora de revisión. Hora actual: {hora_actual.strftime('%H:%M')}")
        print("Próximas horas de revisión:", [hora.strftime('%H:%M') for hora in horas_revision])
    redirect('monitor_services')
    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
        'last_status': last_status  # Enviar los últimos estados a la plantilla
    })


def check_now(request):
    website_status, api_status, soap_status = realizar_revision()
    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
    })


def Login(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'monitorApp/Login.html')


def Home(request):
    return render(request, 'monitorApp/Admin/Home.html')


def SettingsMonitor(request):
    from datetime import datetime, timedelta
    import requests

    URLS = "http://127.0.0.1:8000/api/Settings/"
    data = []

    # Realiza la solicitud GET para obtener configuraciones
    response = requests.get(URLS)
    if response.status_code == 200:
        data = response.json()
        print('Solicitud GET exitosa:', data)
    else:
        print('Error en la solicitud GET, detalles:', response.text)

    # Obtén las próximas revisiones si los datos están disponibles
    proximas_revisiones = []
    if isinstance(data, list) and len(data) > 0:
        config = data[0]
        start_datetime = datetime.fromisoformat(config['start_datetime'])
        interval_hours = int(config['interval_hours'])
        interval_minutes = int(config['interval_minutes'])
        veces=24 * 60 // (interval_hours * 60 + interval_minutes)
        # Calcula las próximas 5 revisiones
        proximas_revisiones = [
            revision.strftime('%H:%M')  # Formatea solo la hora
            for revision in calcular_proximas_revisiones(
                start_datetime, interval_hours, interval_minutes, veces
            )
        ]

    return render(request, 'monitorApp/Admin/SettingsMonitor.html', {
        'settingsConf': data,
        'proximas_revisiones': proximas_revisiones
    })



def logout_view(request):
    logout(request)
    return redirect('Login')


def prueba(request):
    from datetime import datetime, timedelta
    import requests

    URLS = "http://127.0.0.1:8000/api/Settings/"
    data = []

    # Realiza la solicitud GET para obtener configuraciones
    response = requests.get(URLS)
    if response.status_code == 200:
        data = response.json()
        print('Solicitud GET exitosa:', data)
    else:
        print('Error en la solicitud GET, detalles:', response.text)

    # Obtén las próximas revisiones si los datos están disponibles
    proximas_revisiones = []
    if isinstance(data, list) and len(data) > 0:
        config = data[0]
        start_datetime = datetime.fromisoformat(config['start_datetime'])
        interval_hours = int(config['interval_hours'])
        interval_minutes = int(config['interval_minutes'])
        veces=24 * 60 // (interval_hours * 60 + interval_minutes)
        # Calcula las próximas 5 revisiones
        proximas_revisiones = [
            revision.strftime('%H:%M')  # Formatea solo la hora
            for revision in calcular_proximas_revisiones(
                start_datetime, interval_hours, interval_minutes, veces
            )
        ]

    return render(request, 'monitorApp/Admin/prueba.html', {
        'settingsConf': data,
        'proximas_revisiones': proximas_revisiones
    })

    # return render(request, 'monitorApp/Admin/prueba.html')
