from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tratamiento
from .forms import TratamientoForm

@login_required
def lista_tratamientos(request):
    tratamientos = Tratamiento.objects.filter(paciente=request.user)
    return render(request, 'tratamientos/lista_tratamientos.html', {'tratamientos': tratamientos})

@login_required
def crear_tratamiento(request):
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save(commit=False)
            tratamiento.paciente = request.user
            tratamiento.save()
            return redirect('lista_tratamientos')
    else:
        form = TratamientoForm()
    return render(request, 'tratamientos/crear_tratamiento.html', {'form': form})

def editar_tratamiento(request, pk):
    tratamiento = get_object_or_404(Tratamiento, pk=pk)
    if request.method == 'POST':
        form = TratamientoForm(request.POST, instance=tratamiento)
        if form.is_valid():
            form.save()
            return redirect('lista_tratamientos')
    else:
        form = TratamientoForm(instance=tratamiento)
    return render(request, 'tratamientos/editar_tratamiento.html', {'form': form})

def eliminar_tratamiento(request, pk):
    tratamiento = get_object_or_404(Tratamiento, pk=pk)
    if request.method == 'POST':
        tratamiento.delete()
        return redirect('lista_tratamientos')
    return render(request, 'tratamientos/eliminar_tratamiento.html', {'tratamiento': tratamiento})