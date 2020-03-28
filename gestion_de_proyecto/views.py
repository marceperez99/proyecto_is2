from django.shortcuts import render, redirect, get_object_or_404
import datetime
from django.utils import timezone
from gestion_de_proyecto.forms import ProyectoForm
from .models import Proyecto, Participante


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


def participantes_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    lista_participante = proyecto.get_participantes()
    contexto = {'user': request.user, 'lista_participante': lista_participante, 'gerente': proyecto.gerente}
    return render(request, 'gestion_de_proyecto/partipantes.html', context=contexto)


def participante_view(request, proyecto_id, participante_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    participante = get_object_or_404(proyecto.participante_set, pk=participante_id)
    contexto = {'user': request.user, 'participante': participante, }
    return render(request, 'gestion_de_proyecto/participante.html', context=contexto)


def eliminar_participante_view(request, proyecto_id, participante_id):
    participante = get_object_or_404(Participante, id=participante_id)
    usuario = participante.usuario
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        proyecto.eliminar_participante(usuario)
        return redirect('participantes', proyecto_id=proyecto_id)
    contexto = {'user': request.user, 'participante': participante, 'proyecto': proyecto, 'usuario': usuario}
    return render(request, 'gestion_de_proyecto/eliminar_participante.html', context=contexto)
