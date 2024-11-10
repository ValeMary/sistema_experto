from django.db import models
from django.contrib.auth.models import User

class Cita(models.Model):
    ESTADO_CHOICES = [
        ('PROGRAMADA', 'Programada'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas')
    fecha_hora = models.DateTimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PROGRAMADA')

    def __str__(self):
        return f"Cita de {self.paciente.username} el {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        ordering = ['-fecha_hora']