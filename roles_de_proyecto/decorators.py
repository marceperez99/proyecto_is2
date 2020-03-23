from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from gestion_de_proyecto.models import Participante


def pp_requerido(permiso_de_proyecto):
    """
    Decorador de vista que hace que la vista requiera un permiso de proyecto
    Args:

        permiso_de_proyecto: permiso que es necesario para que la vista se ejecute
    """
    def decorador(view):
        def inner(request, proyecto_id):
            participante = Participante.objects.filter(proyecto=proyecto_id).get(usuario=request.user)
            # Se verifica que
            if participante.tiene_pp(permiso_de_proyecto):
                return view(request, proyecto_id)
            else:
                return redirect('pp_insuficientes', id_proyecto=proyecto_id)
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
        def inner(request, proyecto_id, id_fase):
            participante = Participante.objects.filter(proyecto=proyecto_id).get(usuario=request.user)

            if participante.tiene_pp_en_fase(id_fase, permiso_de_proyecto):
                return view(request, proyecto_id, id_fase)
            else:
                return redirect('pp_insuficientes', id_proyecto=proyecto_id)
        return inner
    return decorador
