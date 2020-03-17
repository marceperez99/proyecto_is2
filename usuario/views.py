from django.shortcuts import render
from .models import Usuario
# Create your views here.

def usuarios_view(request):





def usuario_view(request,id_user):
    usuario = Usuario.objects.get(pk=id_user)
    contexto = {'usuario':usuario,'user':request.user}
    return render(request,'usuario/usuario.html',context = contexto)