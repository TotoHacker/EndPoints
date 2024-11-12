from django.db import models
from django.contrib.auth.hashers import make_password

class SysError(models.Model):
    site_url = models.CharField(max_length=100)
    error_site_code = models.CharField(max_length=100)
    date_error = models.DateField()

    def __str__(self):
        return f"{self.site_url} - {self.error_site_code}"
class User(models.Model):
    name_user = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)  
    password_user = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.password_user = make_password(self.password_user)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.name_user