from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from roles_de_proyecto.models import RolDeProyecto
from .forms import NewRolDeProyectoForm


@login_required
#TODO falta incluir el permiso de sistema de que puede ver esto
def listar_roles_de_proyecto_view(request):
    """
    Vista que meustra al usuario la lista de Roles de Proyecto que existen dentro del Sistema.

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
                    for rol in RolDeProyecto.objects.all()
                    ]
                }

    return render(request, 'roles_de_proyecto/listar_roles.html', contexto)

@login_required
def editar_rol_de_proyecto_view(request, id_rol):
    """
    Vista que permite al usuario editar un Rol de Proyecto guardado dentro del sistema.
    :return:
    """
    contexto = {'user': request.user}
    rol = get_object_or_404(RolDeProyecto, pk=id_rol)
    if request.method == 'POST':
        pass
    else:
        form = NewRolDeProyectoForm(instance=rol)
        contexto['form'] = form
        return render(request, 'roles_de_proyecto/editar_rol.html', contexto)


@login_required
#TODO: falta agregar que esta funcion requiere el PS de crear nuevo rol de proyecto
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
    contexto={'user':request.user}
    if request.method == 'POST':
        form = NewRolDeProyectoForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect('nuevo_rol_de_proyecto')
    else:
        contexto['form'] = NewRolDeProyectoForm()

        return render(request, 'roles_de_proyecto/nuevo_rol.html', context=contexto)
