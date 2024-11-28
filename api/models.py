from django.db import models
from django.contrib.auth.models import User  # Usa el modelo de usuario por defecto
from django.utils.timezone import now

class SysError(models.Model):
    site_url = models.CharField(max_length=100)
    error_site_code = models.CharField(max_length=100)
    date_error = models.DateField()

    def __str__(self):
        return f"{self.site_url} - {self.error_site_code}"


class SettingsMonitor(models.Model):
    start_datetime = models.DateTimeField(default=now)  # Fecha y hora de inicio
    interval_hours = models.IntegerField(default=0)  # Intervalo de horas
    interval_minutes = models.IntegerField(default=0)  # Intervalo de minutos

    def __str__(self):
        return f"Inicio: {self.start_datetime}, Intervalo: {self.interval_hours} horas y {self.interval_minutes} minutos"
