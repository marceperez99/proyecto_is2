from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from gestion_de_proyecto.models import Proyecto


def estado_proyecto(*estados):
    """
        Decorador que verifica que el proyecto se encuentre en un estado determinado.

        Si el Proyecto no se encuentra en uno de los estados especificados se redirige al usuario
        a la vista de Visualización del Proyecto.

        Argumentos:
            arg: lista de estados en los que puede estar el Proyecto.
    """

    def decorador(view):
        @wraps(view)
        def inner(request, proyecto_id, *args, **kwargs):
            proyecto = Proyecto.objects.get(id=proyecto_id)
            if proyecto.estado in estados:
                return view(request, proyecto_id, *args, **kwargs)
            else:
                if len(estados) > 1:
                    cadena = " o ".join([", ".join(estados[:-1]), estados[-1]])
                else:
                    cadena = estados[-1]
                messages.error(request, 'El Proyecto debe estar en el Estado ' + cadena)
                return redirect('visualizar_proyecto', proyecto_id)

        return inner

    return decorador
