# api/views.py
from rest_framework import viewsets
from .models import SysError, SettingsMonitor
from .serializers import SysErrorSerializer, UserSerializer, SettingsMonitorSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from django.shortcuts import render
from django.contrib.auth.models import User  # Usa el modelo de usuario por defecto
from django.contrib.auth.decorators import login_required

# Vista para SysError
class SysErrorViewSet(viewsets.ModelViewSet):
    queryset = SysError.objects.all()
    serializer_class = SysErrorSerializer

# Vista para User
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Usando el modelo de usuario por defecto
    serializer_class = UserSerializer

# Vista para SettingsMonitor
class SettingsViewSet(viewsets.ModelViewSet):
    queryset = SettingsMonitor.objects.all()
    serializer_class = SettingsMonitorSerializer

# Vista para Login (si es necesario)
class LoginView(APIView):
    def post(self, request):
        # Obtener el email y la contraseña del cuerpo de la solicitud
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email y contraseña son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar al usuario por email
            user = User.objects.get(email=email)

            # Validar la contraseña usando check_password
            if check_password(password, user.password):
                # Iniciar sesión
                login(request, user)  # Esto requiere un usuario con sesión
                return render(request, 'monitorApp/Admin/Home.html')  # Redirige a una página después del login
            else:
                return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
