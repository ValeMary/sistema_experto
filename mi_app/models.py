from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mi_app_profile')
    # Campos adicionales para el perfil de usuario
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# Puedes añadir más modelos relacionados con el usuario si es necesario
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    receive_notifications = models.BooleanField(default=True)
    theme = models.CharField(max_length=20, default='light')

    def __str__(self):
        return f"{self.user.username}'s preferences"