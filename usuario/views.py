from django.shortcuts import render, get_object_or_404
from .models import Usuario


# Create your views here.

def usuarios_view(request):
    pass


def usuario_view(request, id_usuario):
    usuario = get_object_or_404(Usuario, pk=id_usuario)
    contexto = {'usuario': usuario, 'user': request.user}
    return render(request, 'usuario/usuario.html', context=contexto)
