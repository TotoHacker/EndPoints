from rest_framework import viewsets
from .models import SysError, User
from .serializers import SysErrorSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.shortcuts import render

# Vista para SysError
class SysErrorViewSet(viewsets.ModelViewSet):
    queryset = SysError.objects.all()
    serializer_class = SysErrorSerializer

# Vista para User
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(APIView):
    def post(self, request):
        # Obtener el email y la contraseña del cuerpo de la solicitud
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            # Buscar al usuario por email
            user = User.objects.get(email=email)
            # Verificar si la contraseña proporcionada coincide
            if check_password(password, user.password_user):
                return render(request, 'monitorApp/Admin/Home.html')
            else:
                return Response({"error": "Credenciales inválidas"})
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"})
        
