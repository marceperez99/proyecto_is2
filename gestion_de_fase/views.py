from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from gestion_de_fase.forms import FaseForm
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def visualizar_fase_view(request, proyecto_id, fase_id):
    """
    Vista que permite la visualizacion de una Fase determinada dentro de un proyecto
    Args:
        request: objeto HttpRequest recibido por el servidor.\n
        proyecto_id: int, identificador unico del proyecto.\n
        fase_id: int, identificador unico de la fase que pertenece al proyecto.\n
    Retorna:
        HttpResponse: pagina web correspondiente a la visualizacion de la fase solicitada
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'breadcrumb': {
            'pagina_actual': fase.nombre,
            'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))},
                      {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))}]
        }
    }
    return render(request, 'gestion_de_fase/visualizar_fase.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def listar_fase_view(request, proyecto_id):
    """
    Vista que permite la visualizacion de las fases de un proyecto. Junto con la opcion de crear nuevas Fases dentro del
    proyecto.\n
    Args:
        request: objeto HttpRequest recibido por el servidor,\n
        proyecto_id: int, identificador unico del proyecto.
    Retorna:
        HttpResponse: objeto HttpResponse con la pagina web correspondiente a la lista de Fases de un Proyecto.
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    contexto = {
        'proyecto': proyecto,
        'breadcrumb': {
            'pagina_actual': 'Fases',
            'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))}]
        }
    }
    return render(request, 'gestion_de_fase/listar_fases.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def nueva_fase_view(request, proyecto_id):
    """
    Vista que se usa para la creacion y posicionamiento de una fase dentro de un proyecto
    Si el metodo Http con el que se realizo la peticion fue GET se muestra un formulario para completar.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan en la BD

    Args:

     request: HttpRequest

     proyecto_id: int identificador unico de un Proyecto

    Retorna:

     HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = FaseForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            nuevaFase = form.save(commit=False)
            nuevaFase.proyecto = proyecto
            nuevaFase.fase_cerrada = False
            nuevaFase.puede_cerrarse = False
            nuevaFase.save()
            nuevaFase.posicionar_fase()
            return redirect('listar_fases', proyecto.id)
    else:
        form = FaseForm(proyecto=proyecto)
    contexto = {'formulario': form,
                'breadcrumb': {
                    'pagina_actual': 'Nueva Fase',
                    'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))},
                              {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))}]
                }
                }
    return render(request, 'gestion_de_fase/nueva_fase.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def editar_fase_view(request, proyecto_id, fase_id):
    """
    Vista que muestra al usuario los datos actuales de la fase que se pueden modificar, si el usuario
    desea cambiar, los cambia.
    Si el metodo Http con el que se realizo la peticion fue GET se muestra los datos que tiene la fase con la
    posibilidad de editarlos.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos cambiados y se guardan en la BD

    Args:\n
        request: HttpRequest.
        fase_id: int identificador unico de la fase que se quiere ver. \n
    Retorna:\n
        HttpResponse
    """
    fase = get_object_or_404(Fase, id=fase_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    form = FaseForm(request.POST or None, instance=fase, proyecto=proyecto)
    if request.method == 'POST':
        if form.is_valid():
            fase = form.save(commit=False)
            fase.save()
            fase.posicionar_fase()
            return redirect('listar_fases', proyecto.id)
    contexto = {
        'formulario': form,
        'breadcrumb': {
            'pagina_actual': 'Editar',
            'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))},
                      {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))},
                      {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto_id, fase_id))}]
        }
    }
    return render(request, 'gestion_de_fase/editar_fase.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def eliminar_fase_view(request, proyecto_id, fase_id):
    """
    Muestra una vista al usuario para que confirme la eliminacion de una fase.
    Si el metodo Http con el que se realizo la peticion fue GET se le pide al usuario que confirme la elimincion de una fase.
    Si el metodo Http con el que se realizo la peticion fue POST se procede a eliminar la fase.

    Args:\n
        request: HttpRequest.
        proyecto_id: int identificador unico del Proyecto que se quiere ver. \n
    Retorna:\n
        HttpResponse
    """
    fase = get_object_or_404(Fase, id=fase_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        if proyecto.fase_set.filter(fase_anterior=fase).exists():
            fase_derecha = proyecto.fase_set.get(fase_anterior=fase)
            fase_izquierda = fase.fase_anterior
            fase_derecha.fase_anterior = fase_izquierda
            fase_derecha.save()
        fase.delete()
        # Todo falta pone la url correcta
        return redirect('listar_fases', proyecto.id)
    contexto = {'fase': fase, 'proyecto': proyecto,
                'breadcrumb': {
                    'pagina_actual': 'Eliminar',
                    'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))},
                              {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))},
                              {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto_id, fase_id))}]
                }
                }
    return render(request, 'gestion_de_fase/eliminar_fase.html', contexto)
