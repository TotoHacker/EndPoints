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


def monitor_services(request):
    config = Checktime()
    if not config:
        print("Error al obtener configuraciones de Checktime.")
        return render(request, 'monitorApp/status_list.html', {
            'website_status': [],
            'api_status': [],
            'soap_status': [],
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

    if hora_actual_en_minutos in horas_revision_en_minutos:
        print(f"Hora de revisión: {hora_actual.strftime('%Y-%m-%d %H:%M:%S')}")
        website_status, api_status, soap_status = realizar_revision()
    else:
        print(f"No es hora de revisión. Hora actual: {hora_actual.strftime('%H:%M')}")
        print("Próximas horas de revisión:", [hora.strftime('%H:%M') for hora in horas_revision])

    return render(request, 'monitorApp/status_list.html', {
        'website_status': website_status,
        'api_status': api_status,
        'soap_status': soap_status,
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

    return render(request, 'monitorApp/Admin/SettingsMonitor.html', {'settingsConf': data})


def logout_view(request):
    logout(request)
    return redirect('Login')
