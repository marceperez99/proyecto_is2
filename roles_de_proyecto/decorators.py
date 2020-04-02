from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from gestion_de_proyecto.models import Participante, Proyecto


def pp_requerido(permiso_de_proyecto):
    """
    Decorador de vista que hace que la vista requiera un permiso de proyecto
    Args:

        permiso_de_proyecto: permiso que es necesario para que la vista se ejecute
    """

    def decorador(view):
        @wraps(view)
        def inner(request, proyecto_id, *args, **kwargs):
            try:
                proyecto = Proyecto.objects.get(id=proyecto_id)
                participante = proyecto.get_participante(usuario=request.user)
            except:
                return redirect('pp_insuficientes', proyecto_id)
            # Se verifica que el participante tenga el permiso correspondiente
            #TODO: administrador debe ser trtado especialmente.
            if participante is not None and participante.tiene_pp(permiso_de_proyecto):
                return view(request, proyecto_id, *args, **kwargs)
            else:
                return redirect('pp_insuficientes', proyecto_id)

        return inner

    return decorador


def pp_requerido_en_fase(permiso_de_proyecto):
    """
    Decorador de vista que hace que la vista requiera un permiso de proyecto dentro de una fase de un
    proyecto
    Args:
        permiso_de_proyecto: permiso que es necesario para que la vista se ejecute
    """

    def decorador(view):
        @wraps(view)
        def inner(request, proyecto_id, fase_id, *args, **kwargs):
            try:
                proyecto = Proyecto.objects.get(id=proyecto_id)
                participante = proyecto.get_participante(usuario=request.user)
            except:
                return redirect('pp_insuficientes', proyecto_id)

            if participante is not None and participante.tiene_pp_en_fase(fase_id, permiso_de_proyecto):
                return view(request, proyecto_id, fase_id, *args, **kwargs)
            else:
                return redirect('pp_insuficientes', proyecto_id)

        return inner

    return decorador
