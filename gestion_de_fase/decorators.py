from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from gestion_de_fase.models import Fase


def fase_abierta():
    """
       Decorador que no permite el acceso a una vista si es que la fase del proyecto no esta abierta

    """

    def decorador(view):
        @wraps(view)
        def inner(request, proyecto_id, fase_id, *args, **kwargs):
            fase = Fase.objects.get(id=fase_id)
            if not fase.fase_cerrada:
                return view(request, proyecto_id, fase_id, *args, **kwargs)
            else:
                messages.error(request, 'La fase ya se encuentra cerrada')
                return redirect('visualizar_proyecto', proyecto_id)

        return inner

    return decorador
