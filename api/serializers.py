# api/serializers.py
from rest_framework import serializers
from .models import SysError, User

class SysErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysError
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
