from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from gestion_de_proyecto.forms import ProyectoForm
from .models import Proyecto, Participante

from gestion_de_proyecto.forms import ProyectoForm, NuevoParticipanteForm, SeleccionarPermisosForm
from roles_de_proyecto.decorators import pp_requerido
from roles_de_proyecto.models import RolDeProyecto
from .models import Proyecto


# Create your views here.

def nuevo_proyecto_view(request):
    """
    Vista que se usa para la creacion de un proyecto
    Si el metodo Http con el que se realizo la peticion fue GET se muestra un formulario para completar.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan en la BD

    Args:

        request: HttpRequest

    Retorna:

        HttpResponse
    """
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

    contexto = {'user': request.user, 'lista_participante': lista_participante,'proyecto':proyecto, 'gerente': proyecto.gerente}
    return render(request, 'gestion_de_proyecto/partipantes.html', context=contexto)


def participante_view(request, proyecto_id, participante_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    participante = get_object_or_404(proyecto.participante_set, pk=participante_id)
    if participante.rol is None:
        raise Http404()
    contexto = {'user': request.user, 'participante': participante, 'proyecto': proyecto}
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


def visualizar_proyecto_view(request, proyecto_id):
    """
    Vista que muestra al usuario toda la informacion de un proyecto.

    Args:

        request: HttpRequest
        proyecto_id: int identificador unico del Proyecto que se quiere ver

    Retorna:

        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    contexto = {'user': request.user, 'proyecto': proyecto}
    return render(request, 'gestion_de_proyecto/visualizar_proyecto.html', contexto)


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
                permisos_por_fase = {fase[2:]: request.POST[fase] for fase in request.POST.keys() if
                                     fase.startswith('f_')}
                participante.asignar_permisos_de_proyecto(permisos_por_fase)
                # TODO cambiar a donde dirige este redirect
                return redirect('index')
        else:
            rol = RolDeProyecto.objects.get(id=request.GET['rol'])
            usuario = User.objects.get(id=request.GET['usuario'])
            contexto['seleccionar_permisos_form'] = SeleccionarPermisosForm(usuario, proyecto, rol)

    return render(request, 'gestion_de_proyecto/nuevo_participante.html', contexto)


def pp_insuficientes(request, *args, **kwargs):
    return render(request, 'gestion_de_proyecto/pp_insuficientes.html', context={'user': request.user})
