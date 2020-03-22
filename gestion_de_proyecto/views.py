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
    """
    TODO: falta filtrar todos los usuarios que no son participantes de proyecto
    :param request:
    :param id_proyecto:
    :return:
    """
    proyecto = get_object_or_404(Proyecto, id=id_proyecto)
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
    }
    print(request.GET)
    if len(request.GET.keys()) == 0:
        form = NuevoParticipanteForm()
        form.usuario.queryset = User
        contexto['nuevo_participante_form'] = form
    else:
        if request.method == 'POST':
            print(request.POST)
            form = NuevoParticipanteForm(request.GET)
            if form.is_valid():
                participante = form.save(commit=False)
                participante.proyecto = proyecto
                participante.save()
                permisos_por_fase = {fase[2:]: request.POST[fase] for fase in request.POST.keys() if fase.startswith('f_')}
                print(permisos_por_fase)
                participante.asignar_permisos_de_proyecto(permisos_por_fase)
        else:
            rol = RolDeProyecto.objects.get(id=request.GET['rol'])
            usuario = User.objects.get(id=request.GET['usuario'])
            contexto['seleccionar_permisos_form'] = SeleccionarPermisosForm(usuario, proyecto, rol)

    return render(request, 'gestion_de_proyecto/nuevo_participante.html', contexto)
