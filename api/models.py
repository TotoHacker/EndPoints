from django.db import models
from django.contrib.auth.hashers import make_password,  is_password_usable

from django.utils.timezone import now
class SysError(models.Model):
    site_url = models.CharField(max_length=100)
    error_site_code = models.CharField(max_length=100)
    date_error = models.DateField()

    def __str__(self):
        return f"{self.site_url} - {self.error_site_code}"

class User(models.Model):
    name_user = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    Permissions = models.IntegerField()
    password_user = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Encripta la contraseña si no está encriptada
        if not self.pk and self.password_user:  # Caso de creación
            self.password_user = make_password(self.password_user)
        elif self.pk:  # Caso de actualización
            original_password = User.objects.get(pk=self.pk).password_user
            if self.password_user != original_password:
                self.password_user = make_password(self.password_user)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.name_user
class SettingsMonitor(models.Model):
    
    start_datetime = models.DateTimeField(default=now)  # Fecha y hora de inicio
    interval_hours = models.IntegerField(default=0)  # Intervalo de horas
    interval_minutes = models.IntegerField(default=0)  # Intervalo de minutos

    def __str__(self):
        return f"Inicio: {self.start_datetime}, Intervalo: {self.interval_hours} horas y {self.interval_minutes} minutos"

