import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from monitor.views import load_services_from_xml, check_service_status, check_soap_status, send_email, hora_a_minutos,calcular_horas_revision,horaInicioRevision,minutoInicioRevision, vecesRevision
import datetime
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
            # send_email(subject, sitios_caidos, 'anovelo@thedolphinco.com')
            send_email(subject, sitios_caidos, 'totochucl@gmail.com')

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

def CrudUser(request):
    # GET
    URL = "http://127.0.0.1:8000/api/users/"
    response = requests.get(URL)
    users_data = {}
    if response.status_code == 200:
        users_data = response.json()
        print('Solicitud exitosa')
        print('Data:', users_data)
    else:
        print('Error en la solicitud, detalles:', response.text)

    # CREATE
    DATA = {
        "name_user": "nada",
        "email": "yo@yo.com",
        "password_user": "jejeje"
    }
    create_response = requests.post(URL, json=DATA)
    if create_response.status_code == 201:
        created_data = create_response.json()
        print('Post creado de forma exitosa')
        print('Respuesta:', created_data)
    else:
        print('Error en la solicitud, detalles:', create_response.text)
    
    return render(request, 'monitorApp/Admin/Crud.html', {
        'users_data': users_data,  # Enviar los datos de los usuarios a la vista
        'created_data': created_data if create_response.status_code == 201 else None
    })


def Login(request):
    return render(request, 'monitorApp/Login.html')

def Home(request):
    return render(request, 'monitorApp/Admin/Home.html')

def CrudU(request):
    return render(request,'monitorApp/Admin/Crud.html')