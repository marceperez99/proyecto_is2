from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
import datetime

# Create your views here.
from gestion_de_proyecto.forms import NuevoParticipanteForm, SeleccionarPermisosForm
from gestion_de_proyecto.models import Proyecto, Participante
from roles_de_proyecto.models import RolDeProyecto
from usuario.models import Usuario


def nuevo_proyecto_view(request):
    contexto = {'fecha': datetime.datetime.now(), 'user': request.user}
    return render(request, 'gestion_de_proyecto/nuevo_proyecto.html', context=contexto)


def nuevo_participante_view(request, id_proyecto):
    proyecto = get_object_or_404(Proyecto, id=id_proyecto)
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
    }
    print(request.GET.keys())
    if len(request.GET.keys()) == 0:
        contexto['nuevo_participante_form'] = NuevoParticipanteForm()
    else:
        rol = RolDeProyecto.objects.get(id=request.GET['rol'])
        usuario = User.objects.get(id=request.GET['usuario'])
        contexto['seleccionar_permisos_form'] = SeleccionarPermisosForm(proyecto, rol)
        pass

    return render(request, 'gestion_de_proyecto/nuevo_participante.html', contexto)
