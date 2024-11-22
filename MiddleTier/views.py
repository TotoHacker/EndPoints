import requests
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from monitor.views import (
    load_services_from_xml, check_service_status, 
    check_soap_status, send_email,
    Checktime
)
import datetime
from datetime import datetime, timedelta
from api.models import User



# Función para calcular las próximas horas de revisión
def calcular_proximas_revisiones(start_datetime, interval_hours, interval_minutes, cantidad_revisiones):
    resultados = []
    intervalo = timedelta(hours=interval_hours+12, minutes=interval_minutes)
    proxima_revision = start_datetime   

    for _ in range(cantidad_revisiones):
        resultados.append(proxima_revision)
        proxima_revision += intervalo

    return resultados

# Función principal para monitorear servicios
def monitor_services(request):
    # Obtener configuraciones de Checktime
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

    # Generar las horas de revisión
    horas_revision = calcular_proximas_revisiones(start_datetime, interval_hours, interval_minutes, cantidad_revisiones)
    horas_revision_en_minutos = [hora.hour * 60 + hora.minute for hora in horas_revision]

    # Obtener la hora actual en minutos
    hora_actual = datetime.now()
    hora_actual_en_minutos = hora_actual.hour * 60 + hora_actual.minute

    website_status = []
    api_status = []
    soap_status = []

    # Comprobar si es hora de revisión
    if hora_actual_en_minutos in horas_revision_en_minutos:
        print(f"Hora de revisión: {hora_actual.strftime('%Y-%m-%d %H:%M:%S')}")
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
    else:
        print(f"No es hora de revisión. Hora actual: {hora_actual.strftime('%H:%M')}")
        print("Próximas horas de revisión:", [hora.strftime('%H:%M') for hora in horas_revision])

    # Renderizar resultados
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

        # Actualizar campos del usuario, pero sin tocar la contraseña
        user.name_user = request.POST.get('user-name', user.name_user)
        user.email = request.POST.get('user-email', user.email)
        user.Permissions = request.POST.get('user-Permissions', user.Permissions)

        # Guardamos sin tocar la contraseña
        user.save()

    # Crear usuario
    if request.method == 'POST' and 'user-name' in request.POST:
        data = {
            "name_user": request.POST.get('user-name'),
            "email": request.POST.get('user-email'),
            "password_user": request.POST.get('user-Password'),  # Contraseña en texto plano
            "Permissions": request.POST.get('user-Permissions'),
        }

        # Crear un nuevo usuario usando el modelo o enviar los datos a la API
        response = requests.post(URL, json=data)

        if response.status_code == 201:
            print('Usuario creado con éxito')
            return redirect('Crud')
        else:
            print('Error en la creación del usuario:', response.text)
        
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
        print('Solicitud GET exitosa:', data)
    else:
        print('Error en la solicitud GET, detalles:', response.text)

    # Manejo de actualización con método POST
    if request.method == "POST":
        monitor_id = 1  # ID del objeto que se actualizará
        updated_data = {
            "start_datetime": request.POST.get('start_datetime', ''),
            "interval_hours": request.POST.get('interval_hours', ''),
            "interval_minutes": request.POST.get('interval_minutes', '')
        }

        # Construir la URL dinámica para el monitor específico
        url_put = f"http://127.0.0.1:8000/api/Settings/{monitor_id}/"
        response = requests.put(url_put, json=updated_data)
        if response.status_code == 200:
            print('Configuración actualizada exitosamente')
        else:
            print('Error en la solicitud PUT, detalles:', response.text)

        # Redirigir después de la actualización
        return redirect('Settings')

    # Renderizar la plantilla con los datos obtenidos
    return render(request, 'monitorApp/Admin/SettingsMonitor.html', {'settingsConf': data})
