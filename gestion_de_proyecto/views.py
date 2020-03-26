from django.shortcuts import render, redirect, get_object_or_404
import datetime
from django.utils import timezone
from gestion_de_proyecto.forms import ProyectoForm
from .models import Proyecto

# Create your views here.

def nuevo_proyecto_view(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.fechaDeCreacion = timezone.now()
            proyecto.estado = "En Configuracion"
            proyecto.save()
            return redirect('index')
    else:
        form = ProyectoForm()
    return render(request, 'gestion_de_proyecto/nuevo_proyecto.html', {'formulario': form})


def visualizar_proyecto_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    contexto={'user': request.user, 'proyecto': proyecto}
    return render(request,'gestion_de_proyecto/visualizar_proyecto.html',contexto)