from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from roles_de_sistema.models import RolDeSistema
from usuario.models import Usuario
from .forms import NewRolDeSistemaForm


@login_required
@permission_required('roles_de_sistema.ps_ver_rs', login_url='sin_permiso')
def listar_roles_de_sistema_view(request):
    """
    Vista que muestra al usuario la lista de Roles de Sistema que existen dentro del Sistema.

    Argumentos:
        request: HttpRequest

    Retorna:
        HttpResponse
    """
    contexto = {'user': Usuario.objects.get(id=request.user.id),
                'roles': [
                    {'id': rol.id, 'nombre': rol.nombre, 'descripcion': rol.descripcion,
                     'permisos': [p.name for p in rol.get_permisos()]
                     }
                    for rol in RolDeSistema.objects.all()
                ],
                'breadcrumb': {'pagina_actual': 'Roles de Sistema',
                               'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')}]
                               }
                }

    return render(request, 'roles_de_sistema/listar_roles.html', contexto)


@login_required
@permission_required('roles_de_sistema.pa_editar_rs', login_url='sin_permiso')
def editar_rol_de_sistema_view(request, id_rol):
    """
    Vista que permite al usuario editar un Rol de Sistema guardado dentro del sistema. \n
    Si el metodo Http con el que se realizo la peticion fue GET se muestra la vista de edicion del rol. \n
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan las
    modificaciones.

    Argumentos:
        request: HttpRequest peticion recibida por el servidor \n
        id_rol: int identificador unico del Rol de Sistema que se quiere modificar

    Retorna:
        HttpResponse
    """
    rol = get_object_or_404(RolDeSistema, pk=id_rol)

    if request.method == 'POST':
        form = NewRolDeSistemaForm(request.POST, instance=rol)

        if form.is_valid() and not rol.es_utilizado():
            rs = form.save()
            rs.save()
            messages.success(request, 'Rol de Sistema modificado exitosamente')
            return redirect('rol_de_sistema', id_rol=id_rol)
        else:
            if not form.is_valid():
                messages.error(request, "El formulario no es valido")
            if rol.es_utilizado():
                messages.error(request, "No se Pudo asignar el rol porque existe un usuario con dicho rol")

        contexto = {'user': request.user, 'form': form}
    else:
        contexto = {'user': request.user,
                    'form': NewRolDeSistemaForm(instance=rol, initial={'permisos': [r.id for r in rol.get_permisos()]})
                    }
    contexto['breadcrumb'] = {'pagina_actual': 'Editar',
                              'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                        {'nombre': 'Roles de Sistema', 'url': reverse('listar_roles_de_sistema')},
                                        {'nombre': rol.nombre, 'url': reverse('rol_de_sistema',args= (rol.id,))}]
                              }
    return render(request, 'roles_de_sistema/editar_rol.html', contexto)


@login_required
@permission_required('roles_de_sistema.pa_crear_rs', login_url='sin_permiso')
def nuevo_rol_de_sistema_view(request):
    """
    Vista que permite a un usuario crear un nuevo Rol de Sistema dentro del sistema. \n
    Si al vista recibe un HttpRequest enviado con el metodo GET mostrará al usuario la pantalla de creacion de nuevo
    Rol. \n
    En cambio, si recibe el HttpRequest con el metodo POST tomará los datos recibidos y creará un nuevo Rol de Sistema
    dentro del Sistema. \n
    Esta vista requiere que el usuario haya iniciado sesion y que cuente con el Permiso de Sistema correspondiente para
    crear un nuevo Rol de Sistema.

    Argumentos:
        request: HttpRequest, peticion Http recibida por el servidor de un usuario.

    Retorna:
        HttpResponse
    """
    contexto = {'user': request.user,
                'breadcrumb': {'pagina_actual': 'Nuevo Rol de Sistema',
                               'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                         {'nombre': 'Roles de Sistema', 'url': reverse('listar_roles_de_sistema')}]
                               }
                }

    if request.method == 'POST':
        form = NewRolDeSistemaForm(request.POST)
        if form.is_valid():
            rol = form.save()
            rol.save()

        return redirect('listar_roles_de_sistema')
    else:
        contexto['form'] = NewRolDeSistemaForm()

        return render(request, 'roles_de_sistema/nuevo_rol.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.ps_ver_rs', login_url='sin_permiso')
def rol_de_sistema_view(request, id_rol):
    """
    Vista que muestra al usuario la informacion de un Rol de Sistema.

    Argumentos:
        request: HttpRequest \n
        id_rol: int, identificador unico del Rol de Sistema al que se esta accediendo

    Retorna:
        HttpResponse
    """
    rol = get_object_or_404(RolDeSistema, id=id_rol)

    user = Usuario.objects.get(id=request.user.id)
    contexto = {
        'user': user,
        'permisos': user.get_permisos_list(),
        'rol': {
            'id': rol.id,
            'nombre': rol.nombre,
            'descripcion': rol.descripcion,
            'es_utilizado': rol.es_utilizado(),
            'permisos': [p.name for p in rol.permisos.all()]
        },
        'breadcrumb': {'pagina_actual': rol.nombre,
                       'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                 {'nombre': 'Roles de Sistema', 'url': reverse('listar_roles_de_sistema')}]
                       }

    }
    return render(request, 'roles_de_sistema/ver_rol.html', contexto)


@login_required
@permission_required('roles_de_sistema.pa_eliminar_rs', login_url='sin_permiso')
def eliminar_rol_de_sistema_view(request, id_rol):
    """
    Vista que que se encarga de eliminar un Rol de Sistema si ningun usuario tiene asignado dicho rol

    Argumentos:
        request: HttpRequest \n
        id_rol: int, identificador unico del Rol de Sistema al que se esta accediendo

    Retorna:
        HttpResponse
    """
    rol = get_object_or_404(RolDeSistema, pk=id_rol)
    contexto = {'user': request.user, 'rol': rol,
                'breadcrumb': {'pagina_actual': 'Eliminar Rol',
                               'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                         {'nombre': 'Roles de Sistema', 'url': reverse('listar_roles_de_sistema')},
                                         {'nombre': rol.nombre, 'url': reverse('rol_de_sistema', args=(rol.id,))}]}}

    if request.method == 'POST':
        if rol.es_utilizado():
            messages.error(request, 'El Rol no puede ser eliminado ya que algun usuario tiene asignado este rol.')
            return redirect('rol_de_sistema', id_rol=id_rol)
        else:
            rol.eliminar_rs()
            return redirect('listar_roles_de_sistema')

    return render(request, 'roles_de_proyecto/eliminar_rol.html', contexto)
