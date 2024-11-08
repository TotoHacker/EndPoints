from rest_framework import viewsets
from .models import SysError, User
from .serializers import SysErrorSerializer, UserSerializer

# Vista para SysError
class SysErrorViewSet(viewsets.ModelViewSet):
    queryset = SysError.objects.all()
    serializer_class = SysErrorSerializer

# Vista para User
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
