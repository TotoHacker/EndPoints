from rest_framework import serializers
from django.contrib.auth.models import User  # Usa el modelo de usuario por defecto
from .models import SysError, SettingsMonitor

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
