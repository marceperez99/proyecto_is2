from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from roles_de_sistema.models import RolDeSistema
from .forms import NewRolDeSistemaForm


@login_required
#TODO falta incluir el permiso de sistema de que puede ver esto
def listar_roles_de_sistema_view(request):
    """
    Vista que muestra al usuario la lista de Roles de Sistema que existen dentro del Sistema.

    Args:

     request: HttpRequest

    Retorna:

     HttpResponse
    """
    contexto = {'user': request.user,
                'roles': [
                    {'id':rol.id, 'nombre': rol.nombre, 'descripcion': rol.descripcion,
                     'permisos': [p.name for p in rol.get_permisos()]
                     }
                    for rol in RolDeSistema.objects.all()
                    ]
                }

    return render(request, 'roles_de_sistema/listar_roles.html', contexto)

@login_required
#TODO requiere que se indique que requiere un permiso de sistema
def editar_rol_de_sistema_view(request, id_rol):
    """
    Vista que permite al usuario editar un Rol de Sistema guardado dentro del sistema.
    Si el metodo Http con el que se realizo la peticion fue GET se muestra la vista de edicion del rol.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan las modificaciones

    Args:

        request: HttpRequest peticion recibida por el servidor

        id_rol: int identificador unico del Rol de Sistema que se quiere modificar

    Retorna:

        HttpResponse
    """

    rol = get_object_or_404(RolDeSistema, pk=id_rol)

    if request.method == 'POST':
        form = NewRolDeSistemaForm(request.POST, instance=rol)

        if form.is_valid() and not rol.es_utilizado():
            rs = form.save()
            grupo = Group.objects.get(name=rol.nombre)
            grupo.permissions.clear()
            grupo.permissions.set(rs.get_permisos())
            grupo.name = rs.nombre
            grupo.save()
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

    return render(request, 'roles_de_sistema/editar_rol.html', contexto)


@login_required
#TODO: falta agregar que esta funcion requiere el PS de crear nuevo rol de sistema
def nuevo_rol_de_sistema_view(request):
    """
    Vista que permite a un usuario crear un nuevo Rol de Sistema dentro del sistema.

    Si al vista recibe un HttpRequest enviado con el metodo GET mostrará al usuario la pantalla de creacion de nuevo Rol.

    En cambio, si recibe el HttpRequest con el metodo POST tomará los datos recibidos y creará un nuevo Rol de Sistema dentro del Sistema.

    Esta vista requiere que el usuario haya iniciado sesion y que cuente con el Permiso de Sistema correspondiente
    para crear un nuevo Rol de Sistema.

    Args:

    request: HttpRequest, peticion Http recibida por el servidor de un usuario.

    Retorna:

    HttpResponse
    """
    contexto = {'user': request.user}

    if request.method == 'POST':
        form = NewRolDeSistemaForm(request.POST)
        if form.is_valid():
            rol = form.save()
            group = Group(name=rol.nombre)
            print(rol.get_permisos())
            group.save()
            group.permissions.set(rol.get_permisos())


        return redirect('nuevo_rol_de_sistema')
    else:
        contexto['form'] = NewRolDeSistemaForm()

        return render(request, 'roles_de_sistema/nuevo_rol.html', context=contexto)

def rol_de_sistema_view(request, id_rol):
    """"
    Vista que muestra al usuario la informacion de un Rol de Sistema.

    Args:

        request: HttpRequest

        id_rol: int, identificador unico del Rol de Sistema al que se esta accediendo

    Retorna:

        HttpResponse
    """
    rol = get_object_or_404(RolDeSistema, id=id_rol)
    contexto = {
        'user': request.user,
        'rol': {
            'id': rol.id,
            'nombre': rol.nombre,
            'descripcion': rol.descripcion,
            'es_utilizado': rol.es_utilizado(),
            'permisos': [p.name for p in rol.permisos.all()]
        }
    }
    return render(request, 'roles_de_sistema/ver_rol.html', contexto)


def eliminar_rol_de_sistema_view(request, id_rol):
    rol = get_object_or_404(RolDeSistema, pk=id_rol)
    if request.method == 'POST':
        if rol.es_utilizado():
            messages.error(request, 'El Rol no puede ser eliminado ya que algun usuario tiene asignado este rol.')
            return redirect('rol_de_sistema', id_rol=id_rol)
        else:
            rol.eliminar_rs()
            return redirect('listar_roles')
    else:
        return HttpResponseNotFound('<h1>No se puede acceder a esta pagina.</h1>')
