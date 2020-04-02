from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from roles_de_proyecto.models import RolDeProyecto
from usuario.models import Usuario
from .forms import NewRolDeProyectoForm


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
# TODO falta incluir el permiso de sistema de que puede ver esto
def listar_roles_de_proyecto_view(request):
    """
    Vista que muestra al usuario la lista de Roles de Proyecto que existen dentro del Sistema.

    Args:

     request: HttpRequest

    Retorna:

     HttpResponse
    """
    user = Usuario.objects.get(id=request.user.id)
    contexto = {'user': user,
                'roles': [
                    {'id': rol.id, 'nombre': rol.nombre, 'descripcion': rol.descripcion,
                     'permisos': [p.name for p in rol.get_permisos()]
                     }
                    for rol in RolDeProyecto.objects.all()
                ],
                'breadcrumb': {'pagina_actual': 'Roles de Proyecto',
                               'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')}, ]
                               }
                }

    return render(request, 'roles_de_proyecto/listar_roles.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
# TODO requiere que se indique que requiere un permiso de sistema
def editar_rol_de_proyecto_view(request, id_rol):
    """
    Vista que permite al usuario editar un Rol de Proyecto guardado dentro del sistema.
    Si el metodo Http con el que se realizo la peticion fue GET se muestra la vista de edicion del rol.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan las modificaciones

    Args:

        request: HttpRequest peticion recibida por el servidor

        id_rol: int identificador unico del Rol de Proyecto que se quiere modificar

    Retorna:

        HttpResponse
    """

    rol = get_object_or_404(RolDeProyecto, pk=id_rol)

    if request.method == 'POST':
        form = NewRolDeProyectoForm(request.POST, instance=rol)

        if form.is_valid():  # and not rol.es_utilizado():
            form.save()
            messages.success(request, 'Rol de Proyecto modificado exitosamente')
            return redirect('rol_de_proyecto', id_rol=id_rol)

        contexto = {'user': request.user, 'form': form}
    else:
        contexto = {'user': request.user,
                    'form': NewRolDeProyectoForm(instance=rol, initial={'permisos': [r.id for r in rol.get_permisos()]})
                    }
    contexto['breadcrumb'] = {'pagina_actual': 'Editar Rol',
                              'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                        {'nombre': 'Roles de Proyecto', 'url': reverse('listar_roles_de_proyecto')},
                                        {'nombre': rol.nombre, 'url': reverse('rol_de_proyecto', args=(rol.id,))}]}
    return render(request, 'roles_de_proyecto/editar_rol.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
# TODO: falta agregar que esta funcion requiere el PS de crear nuevo rol de proyecto
def nuevo_rol_de_proyecto_view(request):
    """
    Vista que permite a un usuario crear un nuevo Rol de Proyecto dentro del sistema.

    Si al vista recibe un HttpRequest enviado con el metodo GET mostrará al usuario la pantalla de creacion de nuevo Rol.

    En cambio, si recibe el HttpRequest con el metodo POST tomará los datos recibidos y creará un nuevo Rol de Proyecto dentro del Sistema.

    Esta vista requiere que el usuario haya iniciado sesion y que cuente con el Permiso de Sistema correspondiente
    para crear un nuevo Rol de Proyecto.

    Args:

    request: HttpRequest, peticion Http recibida por el servidor de un usuario.

    Retorna:

    HttpResponse
    """
    contexto = {'user': request.user,
                'breadcrumb': {'pagina_actual': 'Nuevo Rol de Proyecto',
                               'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                         {'nombre': 'Roles de Proyecto', 'url': reverse('listar_roles_de_proyecto')}]
                               }}

    if request.method == 'POST':
        form = NewRolDeProyectoForm(request.POST)
        if form.is_valid():
            rol = form.save()
            rol.permisos.add(Permission.objects.get(codename='pu_ver_proyecto'))
        return redirect('listar_roles_de_proyecto')
    else:
        contexto['form'] = NewRolDeProyectoForm()

        return render(request, 'roles_de_proyecto/nuevo_rol.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def rol_de_proyecto_view(request, id_rol):
    """"
    Vista que muestra al usuario la informacion de un Rol de Proyecto.

    Args:

        request: HttpRequest

        id_rol: int, identificador unico del Rol de Proyecto al que se esta accediendo

    Retorna:

        HttpResponse
    """
    rol = get_object_or_404(RolDeProyecto, id=id_rol)
    user = Usuario.objects.get(id=request.user.id)
    contexto = {
        'user': user,
        'rol': {
            'id': rol.id,
            'nombre': rol.nombre,
            'descripcion': rol.descripcion,
            'es_utilizado': rol.es_utilizado(),
            'permisos': [p.name for p in rol.permisos.all()]
        },
        'breadcrumb': {'pagina_actual': rol.nombre,
                       'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                 {'nombre': 'Roles de Proyecto', 'url': reverse('listar_roles_de_proyecto')}]
                       }
    }
    return render(request, 'roles_de_proyecto/ver_rol.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
def eliminar_rol_de_proyecto_view(request, id_rol):
    """
    Vista de confirmacion de eliminacion de un Proyecto

        Argumentos:
            request: objeto HttpRequest recibido por el servidor
            id_rol: int identificador unico del Rol de Proyecto a eliminar

    """
    rol = get_object_or_404(RolDeProyecto, pk=id_rol)
    contexto = {'user': request.user, 'rol': rol,
                'breadcrumb': {'pagina_actual': 'Eliminar Rol',
                               'links': [{'nombre': 'Panel de Administracion', 'url': reverse('panel_de_control')},
                                         {'nombre': 'Roles de Proyecto', 'url': reverse('listar_roles_de_proyecto')},
                                         {'nombre': rol.nombre, 'url': reverse('rol_de_proyecto', args=(rol.id,))}]}
                }
    if request.method == 'POST':
        if rol.es_utilizado():
            messages.error(request, 'El Rol no puede ser eliminado ya que algun usuario tiene asignado este rol.')
            return redirect('rol_de_proyecto', id_rol=id_rol)
        else:
            rol.delete()
            return redirect('listar_roles_de_proyecto')

    return render(request, 'roles_de_proyecto/eliminar_rol.html', contexto)
