from django.shortcuts import render, get_object_or_404
from gestion_de_proyecto.models import Proyecto
from gestion_de_fase.models import Fase
# Create your views here.

#/poyectos/proyecto_id/fase/fase_id/tipo_de_item/tipo_de_item_id
#/poyectos/proyecto_id/fase/fase_id/tipo_de_item/tipo_de_item_id/editar
#/#/poyectos/proyecto_id/fase/fase_id/tipo_de_item/nuevo
#tipo_de_item/proyecto_id/fase_id

def tipo_de_item_view(request,proyecto_id,fase_id):
    """
    Vista que permite visualizar los tipos de items dentro de una fase de un proyecto

    """

    proyecto = get_object_or_404(Proyecto,pk=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set,pk=fase_id)
    lista_tipo_de_item = list(fase.tipodeitem_set.all())
    contexto = {'user': request.user, 'lista_tipo_de_item': lista_tipo_de_item}
    return render(request,'gestion_de_tipo_de_item/tipos_de_items.html', context=contexto)
