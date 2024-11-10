from django.db import models
from django.contrib.auth.models import User

class Tratamiento(models.Model):
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tratamientos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('EN_CURSO', 'En curso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado')
    ], default='EN_CURSO')

    def __str__(self):
        return f"Tratamiento de {self.paciente.username}: {self.nombre}"

class SeguimientoTratamiento(models.Model):
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE, related_name='seguimientos')
    fecha = models.DateField()
    notas = models.TextField()

    def __str__(self):
        return f"Seguimiento de {self.tratamiento.nombre} el {self.fecha}"
