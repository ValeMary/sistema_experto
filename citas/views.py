from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cita
from .forms import CitaForm

@login_required
def lista_citas(request):
    citas = Cita.objects.filter(paciente=request.user)
    return render(request, 'citas/lista_citas.html', {'citas': citas})

@login_required
def crear_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.paciente = request.user
            cita.save()
            messages.success(request, 'Cita creada exitosamente.')
            return redirect('citas:crear_cita')
    else:
        form = CitaForm()
    return render(request, 'citas/crear_citas.html', {'form': form})

@login_required
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada exitosamente.')
            return redirect('citas:lista_citas')
    else:
        form = CitaForm(instance=cita)
    return render(request, 'citas/editar_cita.html', {'form': form, 'cita': cita})

@login_required
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada exitosamente.')
        return redirect('citas:lista_citas')
    return render(request, 'citas/eliminar_cita.html', {'cita': cita})

 