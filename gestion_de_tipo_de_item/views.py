from django.shortcuts import render
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

    proyecto = Proyecto.objects.get(pk=proyecto_id)
    fase = proyecto.fase_set.get(pk=fase_id)
    lista_tipo_de_item = list(fase.tipodeitem_set.all())
    contexto = {'user': request.user, 'lista_tipo_de_item': lista_tipo_de_item}
    return render('', context=contexto)
