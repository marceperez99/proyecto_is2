from django.shortcuts import render
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

