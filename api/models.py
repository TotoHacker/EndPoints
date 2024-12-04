from django.db import models
from django.contrib.auth.models import User  # Usa el modelo de usuario por defecto
from django.utils.timezone import now

class SysError(models.Model):
    site_url = models.CharField(max_length=100)
    error_site_code = models.CharField(max_length=100)
    date_error = models.DateField()

    def __str__(self):
        return f"{self.site_url} - {self.error_site_code}"

class LastCheckStatus(models.Model):
    service_type = models.CharField(max_length=20)  # Tipo de servicio: 'website', 'api', 'soap'
    service_name = models.CharField(max_length=255)  # Nombre del servicio
    service_url = models.URLField(max_length=255, blank=True, null=True)  # URL del servicio, opcional
    status = models.CharField(max_length=50)  # Estado del servicio: 'Operativo', 'Inactivo', etc.
    response_code = models.CharField(max_length=10)  # Código de respuesta, como HTTP 200
    checked_at = models.DateTimeField(default=now)  # Fecha y hora de la última verificación

    class Meta:
        verbose_name = "Last Check Status"
        verbose_name_plural = "Last Check Statuses"
        ordering = ['-checked_at']  # Ordenar por última revisión primero

    def __str__(self):
        return f"{self.service_type} - {self.service_name} ({self.status})"
    
    
class SettingsMonitor(models.Model):
    start_datetime = models.DateTimeField(default=now)  # Fecha y hora de inicio
    interval_hours = models.IntegerField(default=0)  # Intervalo de horas
    interval_minutes = models.IntegerField(default=0)  # Intervalo de minutos

    def __str__(self):
        return f"Inicio: {self.start_datetime}, Intervalo: {self.interval_hours} horas y {self.interval_minutes} minutos"
