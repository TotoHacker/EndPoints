from rest_framework import serializers
from django.contrib.auth.models import User  
from .models import SysError, SettingsMonitor, LastCheckStatus 

class SysErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysError
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Modelo de usuario por defecto de Django
        fields = '__all__'

class SettingsMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsMonitor
        fields = '__all__'
class last_check_statusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastCheckStatus
        fields = '__all__'
