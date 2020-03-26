from django.shortcuts import render, get_object_or_404
from gestion_de_proyecto.models import Proyecto
from gestion_de_fase.models import Fase
from gestion_de_tipo_de_item.forms import TipoDeItemForm, AtributoCadenaForm, AtributoArchivoForm, AtributoBooleanoForm, \
    AtributoNumericoForm, AtributoFechaForm
from django.utils import timezone


# Create your views here.

# /poyectos/proyecto_id/fase/fase_id/tipo_de_item/tipo_de_item_id
# /poyectos/proyecto_id/fase/fase_id/tipo_de_item/tipo_de_item_id/editar
# /#/poyectos/proyecto_id/fase/fase_id/tipo_de_item/nuevo
# tipo_de_item/proyecto_id/fase_id


def tipo_de_item_view(request, proyecto_id, fase_id):
    """
    Vista que permite visualizar los tipos de items dentro de una fase de un proyecto

    """

    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, pk=fase_id)
    lista_tipo_de_item = list(fase.tipodeitem_set.all())
    contexto = {'user': request.user, 'lista_tipo_de_item': lista_tipo_de_item}
    return render(request, 'gestion_de_tipo_de_item/tipos_de_items.html', context=contexto)


def nuevo_tipo_de_item_view(request, proyecto_id, fase_id):
    """
    TODO: comentar
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, pk=fase_id)
    if request.method == 'POST':
        tipo_de_item_form = TipoDeItemForm(request.POST)
        if tipo_de_item_form.is_valid():
            tipo_de_item = tipo_de_item_form.save(commit=False)
            # tipo_de_item.

            # Lista de atributos dinamicos
            atributos_dinamicos = [dict() for x in range(int(request.POST['cantidad_atributos']))]
            # Se filtran todos los atributos dinamicos
            atributos_de_items = {key: request.POST[key] for key in request.POST if key.startswith("atr_")}
            for atributo in atributos_de_items.keys():
                partes = atributo.split("_", maxsplit=2)
                print(partes)
                atributos_dinamicos[int(partes[1]) - 1][partes[2]] = atributos_de_items[atributo]
            forms = []
            print(atributos_dinamicos)
            for atributo in atributos_dinamicos:
                print(atributo)
                if 'tipo' not in atributo.keys():
                    continue
                if atributo['tipo'] == 'cadena':
                    forms.append(AtributoCadenaForm(atributo))
                elif atributo['tipo'] == 'numerico':
                    forms.append(AtributoNumericoForm(atributo))
                elif atributo['tipo'] == 'booleano':
                    forms.append(AtributoBooleanoForm(atributo))
                elif atributo['tipo'] == 'fecha':
                    forms.append(AtributoFechaForm(atributo))
                elif atributo['tipo'] == 'archivo':
                    forms.append(AtributoArchivoForm(atributo))
            all_valid = True
            for form in forms:
                all_valid = all_valid and form.is_valid()
            # if all( [ form.is_valid() for form in forms ] )

            if all_valid:
                # TODO: poner cosas en tipo de item
                tipo_de_item.fase = Fase.objects.get(pk=fase_id)
                tipo_de_item.creador = request.user
                tipo_de_item.fecha_creacion = timezone.now()
                tipo_de_item.save()

                for form in forms:
                    atributo = form.save(commit=False)
                    atributo.tipo_de_item = tipo_de_item
                    atributo.save()
    else:
        form = TipoDeItemForm()
        form_cadena = AtributoCadenaForm()
        form_archivo = AtributoArchivoForm()
        form_booleano = AtributoBooleanoForm()
        form_numerico = AtributoNumericoForm()
        form_fecha = AtributoFechaForm()
        contexto = {'user': request.user,
                    'proyecto': proyecto,
                    'fase': fase,
                    'form': form,
                    'form_archivo': form_archivo,
                    'form_numerico': form_numerico,
                    'form_booleano': form_booleano,
                    'form_fecha': form_fecha,
                    'form_cadena': form_cadena
                    }
        return render(request, 'gestion_de_tipo_de_item/nuevo_tipo_de_item.html', context=contexto)
