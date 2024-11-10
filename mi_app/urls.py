from django.urls import path
from mi_app import views
from .views import RegisterView

urlpatterns = [
    path("", views.Indexlogin, name="Indexlogin"),
    path("registro/", RegisterView.as_view(), name="registro"),
    path("LogOutIndex/", views.LogOutIndex, name="LogOutIndex"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuario/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuario/borrar/<int:usuario_id>/', views.borrar_usuario, name='borrar_usuario'),
     
]