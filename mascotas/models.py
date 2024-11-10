from django.db import models
from django.utils import timezone

class Sintoma(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class PruebaDiagnostica(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(default='Descripción pendiente')  # Añadimos un valor por defecto
    sintomas = models.ManyToManyField(Sintoma)

    def __str__(self):
        return self.nombre 

class Prevencion(models.Model):
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return self.descripcion

class Enfermedad(models.Model):
    nombre = models.CharField(max_length=100)
    sintomas = models.ManyToManyField(Sintoma)
    pruebas_diagnosticas = models.ManyToManyField(PruebaDiagnostica)
    prevenciones = models.ManyToManyField(Prevencion)
    tratamiento_recomendado = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

from django.core.validators import FileExtensionValidator

class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    propietario = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, default='No especificado')
    direccion = models.TextField(default='Dirección no especificada')
    # ... otros campos
    sintomas = models.ManyToManyField(Sintoma, blank=True)
    enfermedades = models.ManyToManyField(Enfermedad)
    tratamiento = models.TextField(blank=True)
    examen_sangre = models.FileField(upload_to='examenes_sangre/', null=True, blank=True)

    def __str__(self):
        return self.nombre

    def edad(self):
        return timezone.now().year - self.fecha_nacimiento.year

from django.db import models

class PDFDocument(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)   

class ExamenMascota(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='examenes')
    titulo = models.CharField(max_length=200)
    archivo_pdf = models.FileField(upload_to='examenes_mascotas/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.mascota.nombre}"
    

from django.db import models
from .models import Mascota, Enfermedad

class Tratamiento(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='tratamientos')
    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.CASCADE, related_name='tratamientos')
    descripcion = models.TextField()
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)
    medicamentos = models.TextField(blank=True)
    dosis = models.TextField(blank=True)
    frecuencia = models.CharField(max_length=100, blank=True)
    notas = models.TextField(blank=True)
    
    def __str__(self):
        return f"Tratamiento para {self.mascota.nombre} - {self.enfermedad.nombre}"

    class Meta:
        ordering = ['-fecha_inicio']

 