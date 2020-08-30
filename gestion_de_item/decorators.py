from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from gestion_de_item.models import Item


def estado_item(*estados):
    """
        Decorador que verifica que el item se encuentre en un estado determinado.

        Si el Item no se encuentra en uno de los estados especificados se redirige al usuario
        a la vista de Visualización del Proyecto.

        Argumentos:
            arg: lista de estados en los que puede estar el Item.
    """

    def decorador(view):
        @wraps(view)
        def inner(request, proyecto_id, fase_id, item_id, *args, **kwargs):
            item = Item.objects.get(id=item_id)
            if item.estado in estados:
                return view(request, proyecto_id, fase_id, item_id, *args, **kwargs)
            else:
                if len(estados) > 1:
                    cadena = " o ".join([", ".join(estados[:-1]), estados[-1]])
                else:
                    cadena = estados[-1]
                messages.error(request, 'El Item debe estar en el Estado ' + cadena)
                return redirect('visualizar_proyecto', proyecto_id)

        return inner

    return decorador
