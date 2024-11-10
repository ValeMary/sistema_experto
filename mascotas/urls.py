 
from django.urls import path
from . import views

app_name = 'mascotas'  # Esto es crucial para definir el namespace

urlpatterns = [
    
    # Registro de nueva mascota
    path('registrar/', views.registro_mascota, name='registro_mascota'),

    
    path('lista/', views.lista_mascotas, name='lista_mascotas'),
    
    path('editar/<int:pk>/', views.editar_mascota, name='editar_mascota'),
     # Eliminar una mascota específica
    path('eliminar/<int:pk>/', views.eliminar_mascota, name='eliminar_mascota'), 
    
    path('seleccionar-mascota/', views.seleccionar_mascota, name='seleccionar_mascota'),

    path('preparar-detalles/<int:mascota_id>/', views.preparar_detalles_mascota, name='preparar_detalles_mascota'),
   
    path('mascota/<str:mascota_nombre>/', views.detalle_mascota, name='detalle_mascota'),

    path('cargar-examen/<str:mascota_nombre>/', views.cargar_examen, name='cargar_examen'),

    # Lista de enfermedades
    path('enfermedades/', views.lista_enfermedades, name='lista_enfermedades'),
    
    # Detalle de una enfermedad específica
    path('enfermedad/<int:enfermedad_id>/', views.detalle_enfermedad, name='detalle_enfermedad'),

    # Entrenar el modelo de IA
    path('entrenar-modelo/', views.entrenar_modelo, name='entrenar_modelo'),

    path('prediccion-enfermedad/<str:mascota_nombre>/', views.prediccion_enfermedad, name='prediccion_enfermedad'),
    
    path('mascota/<str:mascota_nombre>/guardar-sintomas/', views.guardar_sintomas, name='guardar_sintomas'),
   
    path('mascota/<str:mascota_nombre>/', views.detalle_mascota, name='detalle_mascota'),
    # Mantén la URL existente que usa el ID
    path('mascota/<int:mascota_id>/analizar-examen/', views.analizar_examen, name='analizar_examen'),
    
    path('lista/', views.lista_mascotas, name='lista_mascotas'),

    # Añade la nueva URL que usa el nombre
    path('mascota/<str:mascota_nombre>/analizar-examen/', views.analizar_examen_por_nombre, name='analizar_examen_por_nombre'),
    
    ####################################################################
    path('experto/', views.experto, name='experto'),
    path('eliminar-sintoma/<int:sintoma_id>/', views.eliminar_sintoma, name='eliminar_sintoma'),
    path('tratamientos/', views.lista_tratamientos, name='lista_tratamientos'),
    path('eliminar-tratamiento/<int:tratamiento_id>/', views.eliminar_tratamiento, name='eliminar_tratamiento'),
    ]

