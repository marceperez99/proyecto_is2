from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
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

    usuario = get_object_or_404(User, pk=usuario_id)
    contexto = {'usuario': usuario, 'user': request.user}
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
            return redirect('pefil_de_usuario', usuario_id=usuario.id)
        else:
            messages.error(request, "No se pudo asignar Rol de Sistema")
    else:
        form = AsignarRolDeProyectoForm(usuario=usuario)

    contexto = {'usuario': usuario, 'user': request.user, 'form': form}
    return render(request, 'usuario/asignar_rs.html', contexto)
