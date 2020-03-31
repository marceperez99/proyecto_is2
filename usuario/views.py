from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect

from gestion_de_proyecto.models import Proyecto
from roles_de_proyecto.models import RolDeProyecto
from roles_de_sistema.models import RolDeSistema
from .models import Usuario
from django.contrib import messages

from .forms import AsignarRolDeProyectoForm


# Create your views here.
@login_required
def usuarios_view(request):
    """
    Vista que muestra la lista de usuarios del sistema.


    Require los siguientes permisos de sistema:
        - Visualizar usuarios del sistema.

    """
    lista_usuario = list(User.objects.all())
    contexto = {'lista_usuario': lista_usuario, 'user': request.user}
    return render(request, 'usuario/usuarios.html', context=contexto)


@login_required
def usuario_view(request, usuario_id):
    """
    Vista que permite ver la información publica de un usuario.

    En caso de intentar acceder a un usuario no existente se muestra una pantalla de error


    Requiere los siguientes permisos del sistema:
        -Visualizar usuarios del sistema
    """
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    grupo = None
    if request.method == 'POST':
        usuario.desasignar_rol_a_usuario()
    else:
        for g in usuario.groups.all():
            grupo = g.name
    contexto = {'usuario': usuario, 'user': request.user, 'rs_asignado': usuario.tiene_rs(), 'nombre_rs': grupo}
    return render(request, 'usuario/usuario.html', context=contexto)


@login_required
def usuario_asignar_rol_view(request, usuario_id):
    """
    Vista que permite asignar un rol a un usuario

    En caso de intentar acceder a un usuario no existente se muestra una pantalla de error


    Requiere los siguientes permisos del sistema:
        - Asignar Roles de Sistema
    """
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if request.method == 'POST':
        form = AsignarRolDeProyectoForm(request.POST, usuario=usuario)
        if form.is_valid():
            print(form.cleaned_data.get('Rol'))
            usuario.asignar_rol_a_usuario(form.cleaned_data.get('Rol'))
            return redirect('perfil_de_usuario', usuario_id=usuario.id)
        else:
            messages.error(request, "No se pudo asignar Rol de Sistema")
    else:
        form = AsignarRolDeProyectoForm(usuario=usuario)

    contexto = {'usuario': usuario, 'user': request.user, 'form': form}
    return render(request, 'usuario/asignar_rs.html', contexto)


@login_required
def panel_de_administracion_view(request):
    contexto = {'user': request.user,
                'usuarios': User.objects.all(),
                'proyectos': Proyecto.objects.all(),
                'roles_de_proyecto': RolDeProyecto.objects.all(),
                'roles_de_sistema': RolDeSistema.objects.all(),
                'breadcrumb': {'links': [],
                               'pagina_actual': 'Panel de Administracion'}
                }
    return render(request, 'usuario/panel_de_administracion.html', contexto)
