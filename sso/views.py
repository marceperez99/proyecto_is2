from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def index_view(request):
    """Esta función se encarga de, una vez que el usuario haya iniciado sesión, redirigirla
    al template que muestra el menú pricipal

    Args:
        request (HttpRequest Object): respuesta del request

    Retorna:
        El HttpResponse de la Vista a mostrarse

    """
    contexto = {'user': request.user}
    return render(request, 'sso/index.html', context=contexto)
# Create your views here.

def login_view(request):
    """
    Vista que muestra la pantalla de inicio de sesión. Si el usuario ya ha iniciado sesión, este es redirigido a la pantalla principal del sistema.

    Args:
        request (HttpRequest)

    Retorna:
        HttpResponse
    """
    contexto = None
    if(request.user.is_authenticated):
        return redirect('index')
    else:
        return render(request, 'sso/login.html',context = contexto)