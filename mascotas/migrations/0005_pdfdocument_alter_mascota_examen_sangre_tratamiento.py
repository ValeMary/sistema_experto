# Generated by Django 5.1 on 2024-09-18 22:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mascotas', '0004_examenmascota'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='pdfs/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='mascota',
            name='examen_sangre',
            field=models.FileField(blank=True, null=True, upload_to='examenes_sangre/'),
        ),
        migrations.CreateModel(
            name='Tratamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('medicamentos', models.TextField(blank=True)),
                ('dosis', models.TextField(blank=True)),
                ('frecuencia', models.CharField(blank=True, max_length=100)),
                ('notas', models.TextField(blank=True)),
                ('enfermedad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tratamientos', to='mascotas.enfermedad')),
                ('mascota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tratamientos', to='mascotas.mascota')),
            ],
            options={
                'ordering': ['-fecha_inicio'],
            },
        ),
    ]
