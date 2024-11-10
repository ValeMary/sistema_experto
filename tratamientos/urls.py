from django.urls import path
from . import views

 

urlpatterns = [
    path('', views.lista_tratamientos, name='lista_tratamientos'),
    path('crear/', views.crear_tratamiento, name='crear_tratamiento'),
    path('editar/<int:pk>/', views.editar_tratamiento, name='editar_tratamiento'),
    path('eliminar/<int:pk>/', views.eliminar_tratamiento, name='eliminar_tratamiento'),
]

