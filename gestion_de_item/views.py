from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse

from gestion_de_item.models import Item
from gestion_de_proyecto.models import Proyecto
from roles_de_proyecto.decorators import pp_requerido_en_fase


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pu_f_ver_item')
def listar_items(request, proyecto_id, fase_id):
    """

    :param request:
    :param proyecto_id:
    :param fase_id:
    :return:
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    participante = proyecto.get_participante(request.user)
    print(fase.get_items())
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'items': fase.get_items(),
        'breadcrumb': {'pagina_actual': 'Items',
                       'permisos': participante.get_permisos_por_fase_list(fase),
                       'links': [
                           {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                           {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                           {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))}
                       ]
                       }
    }
    return render(request, 'gestion_de_item/listar_items.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pu_f_ver_item')
def visualizar_item(request, proyecto_id, fase_id, item_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    contexto = {
        'proyecto': proyecto,
        'fase': fase,
        'item': item,
        'breadcrumb': {'pagina_actual': item, 'links': [
            {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
            {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
            {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
            {'nombre': 'Items', 'url': reverse('listar_items', args=(proyecto.id, fase.id))}]}
    }
    return render(request, 'gestion_de_item/ver_item.html', contexto)
    pass
