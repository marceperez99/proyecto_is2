from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from gestion_de_proyecto.forms import ProyectoForm, EditarProyectoForm, NuevoParticipanteForm, SeleccionarPermisosForm, \
    SeleccionarMiembrosDelComiteForm
from roles_de_proyecto.decorators import pp_requerido
from roles_de_proyecto.models import RolDeProyecto
from .models import Proyecto, EstadoDeProyecto, Participante, Comite


# Create your views here.

@login_required
@permission_required('roles_de_sistema.pa_crear_proyecto', login_url='sin_permiso')
def nuevo_proyecto_view(request):
    """
    Vista que se usa para la creacion de un proyecto \n
    Si el metodo Http con el que se realizo la peticion fue GET se muestra un formulario para completar. \n
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan en la BD. \n

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
            proyecto.fecha_de_creacion = timezone.now()
            proyecto.estado = EstadoDeProyecto.CONFIGURACION
            proyecto.save()
            participante = Participante(usuario=proyecto.gerente, proyecto=proyecto)
            participante.save()
            comite = Comite(proyecto=proyecto)
            comite.save()
            return redirect('panel_de_control')
    else:
        form = ProyectoForm()
    contexto = {'formulario': form,
                'breadcrumb': {'pagina_actual': 'Nuevo Proyecto',
                               'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')}]
                               }
                }

    return render(request, 'gestion_de_proyecto/nuevo_proyecto.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pp_ver_participante')
def participantes_view(request, proyecto_id):
    """
    Vista que muestra los nombres y apellidos de los participantes de un proyecto, asi como el nombre del Rol que
    tiene asignado dentro del mismo.

    Argumentos:
        request: HttpRequest \n
        proyecto_id: int identificador único de un proyecto.

    Retorna:
        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    lista_participante = proyecto.get_participantes()

    contexto = {'user': request.user,
                'lista_participante': lista_participante,
                'proyecto': proyecto,
                'gerente': proyecto.gerente,
                'breadcrumb': {'pagina_actual': 'Participantes',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto_id,))}]}
                }
    return render(request, 'gestion_de_proyecto/partipantes.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pp_ver_participante')
def participante_view(request, proyecto_id, participante_id):
    """
    Vista que muestra la siguiente información de un participante de proyecto: \n

    - Nombres y Apellidos.\n
    - Nombre del rol de proyecto asignado. \n
    - Descripción del rol de proyecto asignado. \n
    - Permisos contemplados en el rol asignados a cada fase del proyecto.\n

    En caso de que el id corresponda a un participante eliminado o inexistente se redirige a una pagina 404. \n
    En caso de que el usuario tenga permiso de eliminar participantes dentro del proyecto, se visualiza la opción
    de eliminar.

    Argumentos:
        request: HttpRequest \n
        proyecto_id: int identificador único de un proyecto. \n
        participante_id: int identificador único de un participante a visualizar.

    Retorna:
        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    participante = get_object_or_404(proyecto.participante_set, pk=participante_id)
    if participante.rol is None:
        raise Http404()

    print(participante.get_pp_por_fase())
    contexto = {'user': request.user, 'participante': participante, 'proyecto': proyecto,
                'rol_de_proyecto': {'pp_por_proyecto': participante.rol.get_pp_por_proyecto(),
                                    'pp_por_fase': participante.get_pp_por_fase()},
                'breadcrumb': {'pagina_actual': participante.usuario.get_full_name(),
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto_id,))},
                                         {'nombre': 'Participantes',
                                          'url': reverse('participantes', args=(proyecto_id,))}]}
                }
    return render(request, 'gestion_de_proyecto/participante.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pp_eliminar_participante')
def eliminar_participante_view(request, proyecto_id, participante_id):
    """
    Vista que solicita confirmación del usuario para eliminar un participante de proyecto. \n
    En caso de confirmar la eliminación del participante, regresa a la pagina de visualización de participantes del
    proyecto. \n
    En caso de cancelar la eliminación de participante, regresa a la pagina de visualización del participante.

    Argumentos:
        request: HttpRequest
        proyecto_id : int identificador único de un proyecto.
        participante_id: int identificador único de un participante a eliminar.

    Retorna:
        HttpResponse
    """
    participante = get_object_or_404(Participante, id=participante_id)
    usuario = participante.usuario
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    comite = get_object_or_404(Comite, proyecto=proyecto)
    if comite.es_miembro(participante):
        messages.error(request, 'No se puede eliminar a un participante del Comite de Cambios.')
        return redirect('participante', proyecto_id=proyecto_id, participante_id=participante_id)
    if request.method == 'POST':
        proyecto.eliminar_participante(usuario)
        return redirect('participantes', proyecto_id=proyecto_id)
    contexto = {'user': request.user, 'participante': participante, 'proyecto': proyecto, 'usuario': usuario,
                'breadcrumb': {'pagina_actual': 'Editar',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto',
                                                         args=(proyecto.id,))}]}
                }

    return render(request, 'gestion_de_proyecto/eliminar_participante.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pu_ver_proyecto')
def visualizar_proyecto_view(request, proyecto_id):
    """
    Vista que muestra al usuario toda la informacion de un proyecto.

    Argumentos:
        request: HttpRequest
        proyecto_id: int identificador unico del Proyecto que se quiere ver

    Retorna:
        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    lista_participante = proyecto.participante_set.all().exclude(usuario=proyecto.gerente)
    contexto = {'user': request.user,
                'proyecto': proyecto,
                'breadcrumb': {'pagina_actual': proyecto.nombre}, 'lista_participante': lista_participante}
    return render(request, 'gestion_de_proyecto/visualizar_proyecto.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pg_editar_proyecto')
def editar_proyecto_view(request, proyecto_id):
    """
    Vista que muestra al usuario los datos actuales del proyecto que se pueden modificar, si el usuario
    desea cambiar, los cambia. \n
    Si el metodo Http con el que se realizo la peticion fue GET se muestra los datos que tiene el proyecto con la
    posibilidad de editarlos. \n
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos cambiados y se guardan en la BD

    Argumentos:
        request: HttpRequest. \n
        proyecto_id: int identificador unico del Proyecto que se quiere ver.

    Retorna:
        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    form = EditarProyectoForm(request.POST or None, instance=proyecto)
    if request.method == 'POST':
        proyecto = form.save(commit=False)
        proyecto.save()
        return redirect('index')
    contexto = {'formulario': form, 'breadcrumb': {'pagina_actual': 'Editar',
                                                   'links': [{'nombre': proyecto.nombre,
                                                              'url': reverse('visualizar_proyecto',
                                                                             args=(proyecto.id,))}]}}
    return render(request, 'gestion_de_proyecto/editar_proyecto.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def cancelar_proyecto_view(request, proyecto_id):
    """
    Muestra una vista al usuario para que confirme la cancelacion del proyecto. \n
    Si el metodo Http con el que se realizo la peticion fue GET se le pide al usuario que confirme la cancelacion
    del proyecto. \n
    Si el metodo Http con el que se realizo la peticion fue POST se procede a cambiar el estado del proyecto a
    "Cancelado".

    Argumentos:
        request: HttpRequest. \n
        proyecto_id: int identificador unico del Proyecto que se quiere ver.

    Retorna:
        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if not request.user.has_perm('roles_de_sistema.pa_cancelar_proyecto'):
        if not request.user == proyecto.gerente:
            return redirect('pp_insuficientes', proyecto_id)

    if request.method == 'POST':
        if proyecto.cancelar():
            proyecto.save()
        else:
            messages.error(request, 'No se puede cancelar un proyecto en estado "Finalizado".')
        return redirect('index')
    return render(request, 'gestion_de_proyecto/cancelar_proyecto.html', {'proyecto': proyecto})


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pg_iniciar_proyecto')
def iniciar_proyecto_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        if proyecto.iniciar():
            proyecto.save()
        else:
            messages.error(request, 'No se puede iniciar el proyecto.')
        return redirect('visualizar_proyecto', proyecto_id)
    return render(request, 'gestion_de_proyecto/iniciar_proyecto.html', {'proyecto': proyecto})


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pp_agregar_participante')
def nuevo_participante_view(request, proyecto_id):
    """
    Vista que permite la asignacion de un rol

    Argumentos:
        request: HttpRequest recibido por el servidor \n
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
                rol = participante.rol
                # Si ya existe una instancia de la clase Participante con el usuario en cuestion se obtiene ese objeto
                if proyecto.participante_set.all().filter(usuario=participante.usuario).exists():
                    participante = proyecto.participante_set.get(usuario=participante.usuario)
                else:
                    # En caso contrario se incluyen los campos faltantes y se guarda el objeto participante
                    # obtenido del formulario
                    participante.proyecto = proyecto
                    participante.save()
                permisos_por_fase = {fase[2:]: request.POST.getlist(fase) for fase in request.POST.keys() if
                                     fase.startswith('f_')}
                for fase in permisos_por_fase.keys():
                    permisos_por_fase[fase].append('pu_f_ver_fase')

                # Se asigna el rol de proyecto con los permisos correspondientes
                participante.asignar_rol_de_proyecto(rol, permisos_por_fase)

                return redirect('participantes', proyecto_id)
        else:
            rol = RolDeProyecto.objects.get(id=request.GET['rol'])
            usuario = User.objects.get(id=request.GET['usuario'])
            contexto['seleccionar_permisos_form'] = SeleccionarPermisosForm(usuario, proyecto, rol)
    contexto['breadcrumb'] = {'pagina_actual': 'Nuevo Participante',
                              'links': [{'nombre': proyecto.nombre,
                                         'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                        {'nombre': 'Participantes',
                                         'url': reverse('participantes', args=(proyecto_id,))}]
                              }
    return render(request, 'gestion_de_proyecto/nuevo_participante.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pp_asignar_rp_a_participante')
def asignar_rol_de_proyecto_view(request, proyecto_id, participante_id):
    """
    Vista que permite la asignacion de un nuevo Rol de Proyecto a un participante del proyecto
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    participante = get_object_or_404(proyecto.participante_set, id=participante_id)
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'participante': participante,
        'roles_de_proyecto': RolDeProyecto.objects.all(),
        'breadcrumb': {'pagina_actual': 'Asignar Rol de Proyecto',
                       'links': [
                           {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                           {'nombre': 'Participantes', 'url': reverse('participantes', args=(proyecto.id,))},
                           {'nombre': participante.usuario.get_full_name(),
                            'url': reverse('participante', args=(proyecto_id, participante_id))}]
                       }
    }
    if 'rol_de_proyecto' in request.GET.keys():
        rol = get_object_or_404(RolDeProyecto, id=request.GET['rol_de_proyecto'])
        contexto['seleccionar_permisos_form'] = SeleccionarPermisosForm(participante.usuario, proyecto, rol)
    if request.method == 'POST':
        permisos_por_fase = {fase[2:]: request.POST.getlist(fase) for fase in request.POST.keys() if
                             fase.startswith('f_')}

        for fase in permisos_por_fase.keys():
            permisos_por_fase[fase].append('pu_f_ver_fase')

        rol = get_object_or_404(RolDeProyecto, id=request.POST['rol'])
        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)
        return redirect('participante', proyecto.id, participante.id)
    return render(request, 'gestion_de_proyecto/asignar_rol_de_proyecto.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def pp_insuficientes(request, *args, **kwargs):
    """
    Vista que se muestra al usuario al detectar que este trata de realizar una accion para la que no tiene permisos
    dentro del proyecto.

    Argumentos:
        request: objeto HttpRequest recibido por el servidor.
    Retorna:
        HttpResponse: pagina HTML que indica al usuario que no tiene los permisos de proyecto correspondientes.
    """
    return render(request, 'gestion_de_proyecto/pp_insuficientes.html', context={'user': request.user})


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pg_asignar_comite')
def seleccionar_miembros_del_comite_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    comite = get_object_or_404(Comite, proyecto=proyecto)
    form = SeleccionarMiembrosDelComiteForm(proyecto, instance=comite)
    contexto = {'user': request.user, 'form': form,
                'breadcrumb': {'pagina_actual': 'Asignar Comite de Cambios',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Comite de Cambios', 'url': '#'}]
                               }
                }
    if request.method == 'POST':
        form = SeleccionarMiembrosDelComiteForm(proyecto, request.POST, instance=comite)
        if form.is_valid():
            comite.miembros.clear()
            for participante in form.cleaned_data['miembros']:
                comite.miembros.add(participante)
            comite.save()
            return redirect('visualizar_proyecto', proyecto_id=proyecto_id)
    return render(request, 'gestion_de_proyecto/seleccionar_miembros_del_comite.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.ps_ver_proyecto', login_url='sin_permiso')
def info_proyecto_view(request, proyecto_id):
    """
    Metodo que muestra una pantalla de visualizacion de la informacion en general de un proyecto del sistema.\n
    Retorna:
        HttpResponse: respuesta HTTP a la solicitud del usuario.
    """

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    participante = proyecto.get_participante(request.user)
    contexto = {'user': request.user, 'proyecto': proyecto,
                'participante': participante,
                'breadcrumb': {'pagina_actual': 'Informacion del Proyecto',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))}]}}

    return render(request, 'gestion_de_proyecto/info_proyecto.html', contexto)
