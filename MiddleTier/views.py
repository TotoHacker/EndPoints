import requests
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from monitor.views import (
    load_services_from_xml, check_service_status, 
    check_soap_status, send_email, hora_a_minutos,
    calcular_horas_revision, Checktime
)
import datetime
from api.models import User
# Vista principal para monitorear los servicios
def monitor_services(request):
    time_settings = Checktime(request)
    horaInicioRevision = time_settings['horaInicioRevision']
    minutoInicioRevision = time_settings['minutoInicioRevision']
    vecesRevision = time_settings['vecesRevision']

    hora_actual = datetime.datetime.now()
    hora_actual_en_minutos = hora_a_minutos(hora_actual.hour, hora_actual.minute)
    horas_revision_en_minutos = calcular_horas_revision(horaInicioRevision, minutoInicioRevision, vecesRevision)

    website_status  = []
    api_status = []
    soap_status = []

    if hora_actual_en_minutos in horas_revision_en_minutos:
        websites, apis, soap_services = load_services_from_xml()

        website_status = [check_service_status(service) for service in websites]
        api_status = [check_service_status(api) for api in apis]
        soap_status = [check_soap_status(soap) for soap in soap_services]

        sitios_caidos = [
            {
                'name': service['name'], 
                'code': service['code'],
                'url': service.get('url', 'URL no disponible')
            }
            for service in website_status 
            if service['status'] != 'Operativo'
        ]

        if sitios_caidos:
            subject = "Servicios caídos en el monitor"
            send_email(subject, sitios_caidos, 'totochucl@gmail.com')

            for sitio in sitios_caidos:
                URL = "http://127.0.0.1:8000/api/syserrors/"
                DATA = {
                    "site_url": sitio['url'], 
                    "error_site_code": sitio['code'], 
                    "date_error": datetime.datetime.now().strftime("%Y-%m-%d")
                }

                response = requests.post(URL, json=DATA)
                if response.status_code == 200:
                    print('Solicitud exitosa')
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
def CreateUser(request):
    URL="http://127.0.0.1:8000/api/users/"
    DATA={
        "name_user": "",
        "email": "",
        "password_user": ""
    }
    response = requests.post(URL, json=DATA)
    if response.status_code == 201:
        data = response.json()
        print('Post creado de forma exitosa')
        print('Respuesta:', data)
    else:
        print('Error en la solicitud, detalles:', response.text)
    return render(request, 'monitorApp/Admin/Crud.html', {'UserCreate': DATA})

# Otras vistas
def Login(request):
    return render(request, 'monitorApp/Login.html')

#edit user


def Home(request):
    return render(request, 'monitorApp/Admin/Home.html')


def CrudU(request):
    # Obtener todos los usuarios desde la API
    URL = "http://127.0.0.1:8000/api/users/"
    response = requests.get(URL)
    users_data = []

    if response.status_code == 200:
        users_data = response.json()
    else:
        print('Error en la solicitud, detalles:', response.text)

    # Manejo de la edición de usuario
    if request.method == 'POST' and 'user-id' in request.POST:
        user_id = request.POST.get('user-id')
        user = get_object_or_404(User, id=user_id)

        # Actualizar campos del usuario
        user.name_user = request.POST.get('user-name', user.name_user)
        user.email = request.POST.get('user-email', user.email)
        user.save()

        # Redirigir para evitar reenvío de formulario
        return redirect('Crud')  

    return render(request, 'monitorApp/Admin/Crud.html', {'users_data': users_data})
def CrudE(request):
    URLE = "http://127.0.0.1:8000/api/syserrors/"
    response = requests.get(URLE)
    Error_data = []

    if response.status_code == 200:
        Error_data = response.json()
    else:
        print('Error en la solicitud, detalles:', response.text)

    # Manejo de eliminación
    if request.method == 'POST' and 'error-id' in request.POST:
        error_id = request.POST.get('error-id')
        delete_url = f"{URLE}{error_id}/"  # Asumiendo que la API acepta DELETE en esta URL
        delete_response = requests.delete(delete_url)
        if delete_response.status_code == 200:
            print(f"Error {error_id} eliminado correctamente.")
             
        else:
            print(f"Error al eliminar el error {error_id}: {delete_response.text}")
        return redirect('CrudErrors') 
    return render(request, 'monitorApp/Admin/CrudErrors.html', {'Errors_data': Error_data})

def SettingsMonitor(request):
    URLS = "http://127.0.0.1:8000/api/Settings/"
    data = []  # Inicializamos la variable 'data' como lista vacía

    # Solicitud GET para obtener los datos
    response = requests.get(URLS)
    if response.status_code == 200:
        data = response.json()
        print('Solicitud exitosa')
    else:
        print('Error en la solicitud, detalles:', response.text)

    # Actualización de datos con PUT
    if request.method == "POST":
        monitor_id = 1  
        updated_data = {
            "hour": request.POST.get('hour', ''),
            "minutes": request.POST.get('minutes', ''),
            "timesReview": request.POST.get('timesReview', '')
        }
        # Construir la URL dinámica para el monitor específico
        url_put = f"http://127.0.0.1:8000/api/Settings/{monitor_id}/"
        response = requests.put(url_put, json=updated_data)
        if response.status_code == 200:
            print('Post actualizado de forma exitosa')
        else:
            print('Error en la solicitud PUT, detalles:', response.text)
        return redirect('CrudErrors') 
    return render(request, 'monitorApp/Admin/SettingsMonitor.html', {'settingsConf': data})
