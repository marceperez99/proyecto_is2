from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from .models import Usuario


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
