import requests
from django.shortcuts import render, redirect
from monitor.views import (
    load_services_from_xml, check_service_status,
    check_soap_status, send_email,InitialStatus
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
    websites, apis, soap_services,count = load_services_from_xml()
    countdown=0
    # Comprobar estados
    website_status = [check_service_status(service) for service in websites]
    api_status = [check_service_status(api) for api in apis]
    soap_status = [check_soap_status(soap) for soap in soap_services]
    total_response_time=0
    n=0
    sitios_caidos = []
    # Identificar sitios caídos
    for service in website_status:
        if service['status'] != 'Operativo':
            sitios_caidos.append({
                'name': service['name'],
                'code': service['code'],
                'url': service.get('url', 'URL no disponible')
            })
            countdown += 1  
        if service.get('response_time')!='N/A':
            response_time = float(service.get('response_time', 0) or 0)
            total_response_time += response_time
            n=n+1
        PromTime=total_response_time/5/n
        
    print('response',total_response_time,n)

    # Enviar notificaciones si hay sitios caídos
    if sitios_caidos:
        subject = "Servicios caídos en el monitor"
        send_email(subject, sitios_caidos, '')

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

    return website_status, api_status, soap_status,count,countdown,PromTime

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
        website_status, api_status, soap_status,count,countdown,PromTime = realizar_revision()
    else:
        print(f"No es hora de revisión. Hora actual: {hora_actual.strftime('%H:%M')}")
        print("Próximas horas de revisión:", [hora.strftime('%H:%M') for hora in horas_revision])
        countdown=0
        PromTime=0
        website_status, api_status, soap_status, count = InitialStatus()  

    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
        'last_status': last_status,
        'count' :count,
        'countdown':countdown,
        'PromTime':PromTime
    })

def check_now(request):
    website_status, api_status, soap_status, count, countdown, PromTime = realizar_revision()
    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
        'count' :count,
        'countdown':countdown,
        'PromTime':PromTime
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

    response = requests.get(URLS)
    if response.status_code == 200:
        data = response.json()
        print('Solicitud GET exitosa:', data)
    else:
        print('Error en la solicitud GET, detalles:', response.text)

    if request.method == "POST":
        monitor_id = 1
        updated_data = {
            "start_datetime": request.POST.get('start_datetime', ''),
            "interval_hours": request.POST.get('interval_hours', ''),
            "interval_minutes": request.POST.get('interval_minutes', '')
        }

        url_put = f"http://127.0.0.1:8000/api/Settings/{monitor_id}/"
        response = requests.put(url_put, json=updated_data)
        if response.status_code == 200:
            print('Configuración actualizada exitosamente')
        else:
            print('Error en la solicitud PUT, detalles:', response.text)

        return redirect('Settings')
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
        
        website_status, api_status, soap_status = InitialStatus()  # Desestructurar la tupla directamente

    return render(request, 'monitorApp/Admin/prueba.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
        'last_status': last_status  # Enviar los últimos estados a la plantilla
    })

