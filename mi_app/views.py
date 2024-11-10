from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required 
import os
from django.conf import settings
import logging
from django.contrib import messages
from .forms import RegistroForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User 
#--------------------------------------------------# 

@login_required
def lista_usuarios(request):
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'registration/lista_usuarios.html', {'usuarios': usuarios})



logger = logging.getLogger(__name__)


def Indexlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirige al dashboard después del login exitoso
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    template_path = os.path.join(settings.BASE_DIR, 'mi_app', 'templates', 'registration', 'login.html')
    logger.info(f"Buscando template en: {template_path}")
    return render(request, 'registration/login.html')
 
 
from django.contrib import messages
from .forms import RegistroForm

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión al usuario inmediatamente después de registrarse
            messages.success(request, "Registro exitoso. Bienvenido!")
            return redirect('dashboard')  # Redirige al dashboard o a donde prefieras
        else:
            messages.error(request, "Error en el registro. Por favor, verifica la información.")
    else:
        form = RegistroForm()
    
    return render(request, 'register.html', {'form': form})



@login_required
def dashboard(request):
    return render(request, "registration/dashboard.html")    



def LogOutIndex(request):
    logout(request)
    return HttpResponseRedirect("/")      

 

 
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

class RegisterView(CreateView):
    form_class = RegistroForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('dashboard')  # Cambiado a 'dashboard'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)  # Inicia sesión al usuario
        messages.success(self.request, "Registro exitoso. Bienvenido!")
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)
    

@login_required
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = RegistroForm(instance=usuario)
    return render(request, 'registration/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
def borrar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f'Usuario {usuario.username} eliminado correctamente.')
        return redirect('lista_usuarios')
    return render(request, 'registration/confirmar_borrar_usuario.html', {'usuario': usuario})
 
 
 