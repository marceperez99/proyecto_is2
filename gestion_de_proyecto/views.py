from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, get_object_or_404
import datetime
from gestion_de_proyecto.forms import NuevoParticipanteForm, SeleccionarPermisosForm
from gestion_de_proyecto.models import Proyecto
from roles_de_proyecto.decorators import pp_requerido
from roles_de_proyecto.models import RolDeProyecto


def nuevo_proyecto_view(request):
    contexto = {'fecha': datetime.datetime.now(), 'user': request.user}
    return render(request, 'gestion_de_proyecto/nuevo_proyecto.html', context=contexto)


@pp_requerido('pp_agregar_participante')
def nuevo_participante_view(request, proyecto_id):
    """
    Vista que permite la asignacion de un rol

    Args

    request: HttpRequest recibido por el servidor
    proyecto_id: identificador del proyecto donde se agregara el usuario

    Retorna

    HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
    }

    if len(request.GET.keys()) == 0:
        form = NuevoParticipanteForm(proyecto=proyecto)
        contexto['nuevo_participante_form'] = form
    else:
        if any(arg not in request.GET.keys() for arg in ['rol', 'usuario']):
            raise Http404('No se pasaron los argumentos correctos a la URL')
        if request.method == 'POST':
            form = NuevoParticipanteForm(request.GET)
            if form.is_valid():
                participante = form.save(commit=False)
                participante.proyecto = proyecto
                participante.save()
                permisos_por_fase = {fase[2:]: request.POST[fase] for fase in request.POST.keys() if fase.startswith('f_')}
                participante.asignar_permisos_de_proyecto(permisos_por_fase)
        else:
            rol = RolDeProyecto.objects.get(id=request.GET['rol'])
            usuario = User.objects.get(id=request.GET['usuario'])
            contexto['seleccionar_permisos_form'] = SeleccionarPermisosForm(usuario, proyecto, rol)

    return render(request, 'gestion_de_proyecto/nuevo_participante.html', contexto)


def pp_insuficientes(request, *args, **kwargs):
    return render(request, 'gestion_de_proyecto/pp_insuficientes.html', context={'user': request.user})
