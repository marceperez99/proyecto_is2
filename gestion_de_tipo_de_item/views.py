from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from gestion_de_proyecto.models import Proyecto
from gestion_de_fase.models import Fase
from gestion_de_tipo_de_item.forms import TipoDeItemForm, AtributoCadenaForm, AtributoArchivoForm, AtributoBooleanoForm, \
    AtributoNumericoForm, AtributoFechaForm
from gestion_de_tipo_de_item.models import TipoDeItem
from gestion_de_tipo_de_item.utils import guardar_atributos, guardar_tipo_de_item, atributo_form_handler, \
    construir_atributos, recolectar_atributos

# Create your views here.

# /poyectos/proyecto_id/fase/fase_id/tipo_de_item/tipo_de_item_id
# /poyectos/proyecto_id/fase/fase_id/tipo_de_item/tipo_de_item_id/editar
# /#/poyectos/proyecto_id/fase/fase_id/tipo_de_item/nuevo
# tipo_de_item/proyecto_id/fase_id
from gestion_de_tipo_de_item.utils import get_dict_tipo_de_item


def tipo_de_item_view(request, proyecto_id, fase_id, tipo_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    tipo_de_item = get_object_or_404(fase.tipodeitem_set, id=tipo_id)

    contexto = {'user': request.user,
                'proyecto': proyecto,
                'fase': fase,
                'tipo_de_item': get_dict_tipo_de_item(tipo_de_item),
                'breadcrumb': {'pagina_actual': tipo_de_item.nombre,
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Tipos de Item',
                                          'url': reverse('tipos_de_item', args=(proyecto.id, fase.id))},
                                         ]
                               }
                }

    return render(request, 'gestion_de_tipo_de_item/ver_tipo_de_item.html', contexto)


def listar_tipo_de_item_view(request, proyecto_id, fase_id):
    """
    Vista que permite visualizar los tipos de items dentro de una fase de un proyecto

    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, pk=fase_id)
    lista_tipo_de_item = list(fase.tipodeitem_set.all())
    contexto = {'user': request.user,
                'proyecto': proyecto,
                'fase': fase,
                'lista_tipo_de_item': lista_tipo_de_item,
                'breadcrumb': {'pagina_actual': 'Tipos de Item',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))}]
                               }
                }
    return render(request, 'gestion_de_tipo_de_item/tipos_de_items.html', context=contexto)


def nuevo_tipo_de_item_view(request, proyecto_id, fase_id, tipo_de_item_id=None):
    """
    TODO: comentar
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, pk=fase_id)
    contexto = {'user': request.user,
                'proyecto': proyecto,
                'fase': fase,
                'tipos_de_atributo_forms': {'cadena': AtributoCadenaForm(), 'archivo': AtributoArchivoForm(),
                                            'booleano': AtributoBooleanoForm(), 'numerico': AtributoNumericoForm(),
                                            'fecha': AtributoFechaForm()},
                'breadcrumb': {'pagina_actual': 'Nuevo',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Tipos de Item',
                                          'url': reverse('tipos_de_item', args=(proyecto.id, fase.id))},
                                         ]
                               }
                }

    if request.method == 'POST':

        tipo_de_item_form = TipoDeItemForm(request.POST or None)
        if tipo_de_item_form.is_valid():
            tipo_de_item = tipo_de_item_form.save(commit=False)
            atributos_dinamicos = construir_atributos(request)
            atributos_forms = atributo_form_handler(atributos_dinamicos)

            all_valid = True
            # Se validan todos los forms
            for form in atributos_forms:
                all_valid = all_valid and form.is_valid()

            if all_valid:
                # TODO: Sobrecargar el save del form.
                guardar_tipo_de_item(tipo_de_item, fase, request.user)
                guardar_atributos(atributos_forms, tipo_de_item)

                return redirect('tipos_de_item', proyecto_id=proyecto_id, fase_id=fase_id)
            else:
                contexto['form'] = tipo_de_item_form
                contexto['atributos_seleccionados'] = atributos_forms
    else:
        if tipo_de_item_id is None:
            contexto['form'] = TipoDeItemForm()
        else:
            tipo_de_item = get_object_or_404(TipoDeItem, id=tipo_de_item_id)
            contexto['form'] = TipoDeItemForm(request.POST or None, instance=tipo_de_item)
            # TODO: mañantipoa
            # Construye un diccionario a partir de la lista de atributos

            atributos_dinamicos = recolectar_atributos(tipo_de_item)
            print(atributos_dinamicos)
            atributos_forms = atributo_form_handler(atributos_dinamicos)
            print(atributos_forms)
            contexto['atributos_seleccionados'] = atributos_forms
    return render(request, 'gestion_de_tipo_de_item/nuevo_tipo_de_item.html', context=contexto)


def importar_tipo_de_item_view(request, proyecto_id, fase_id):
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    fase = get_object_or_404(Fase, pk=fase_id)
    lista_tipo_de_item = [get_dict_tipo_de_item(tipo) for tipo in TipoDeItem.objects.exclude(fase=fase)]

    contexto = {'user': request.user,
                'lista_tipo_de_item': lista_tipo_de_item,
                'proyecto': proyecto, 'fase': fase,
                'breadcrumb': {'pagina_actual': 'Importar',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Tipos de Item',
                                          'url': reverse('tipos_de_item', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Nuevo',
                                          'url': reverse('nuevo_tipo_de_item', args=(proyecto.id, fase.id))},
                                         ]
                               }
                }
    return render(request, 'gestion_de_tipo_de_item/importar_tipo_de_item.html', context=contexto)


def editar_tipo_de_item_view(request, proyecto_id, fase_id, tipo_de_item_id):
    """
    TODO: comentar
    """
    # Aca se verifica que no existan item de este tipo
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, pk=fase_id)
    tipo_de_item = get_object_or_404(fase.tipodeitem_set, id=tipo_de_item_id)
    contexto = {'user': request.user,
                'proyecto': proyecto,
                'fase': fase,
                'tipos_de_atributo_forms': {'cadena': AtributoCadenaForm(), 'archivo': AtributoArchivoForm(),
                                            'booleano': AtributoBooleanoForm(), 'numerico': AtributoNumericoForm(),
                                            'fecha': AtributoFechaForm()},
                'breadcrumb': {'pagina_actual': 'Editar',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto_id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Tipos de Item',
                                          'url': reverse('tipos_de_item', args=(proyecto.id, fase.id))},
                                         {'nombre': tipo_de_item.nombre,
                                          'url': reverse('tipo_de_item', args=(proyecto_id, fase_id, tipo_de_item_id))}
                                         ]
                               }
                }

    if request.method == 'POST':
        tipo_de_item_form = TipoDeItemForm(request.POST or None)
        if tipo_de_item_form.is_valid():
            tipo_de_item = tipo_de_item_form.save(commit=False)
            atributos_dinamicos = construir_atributos(request)
            atributos_forms = atributo_form_handler(atributos_dinamicos)

            all_valid = True
            # Se validan todos los forms
            for form in atributos_forms:
                all_valid = all_valid and form.is_valid()

            if all_valid:
                # TODO: Sobrecargar el save del form.
                guardar_tipo_de_item(tipo_de_item, fase, request.user)
                guardar_atributos(atributos_forms, tipo_de_item)
                tipo_de_item = TipoDeItem.objects.get(id=tipo_de_item_id)
                tipo_de_item.delete()

                return redirect('tipos_de_item', proyecto_id=proyecto_id, fase_id=fase_id)
            else:
                contexto['form'] = tipo_de_item_form
                contexto['atributos_seleccionados'] = atributos_forms
    else:
        if tipo_de_item_id is None:
            contexto['form'] = TipoDeItemForm()
        else:
            tipo_de_item = get_object_or_404(TipoDeItem, id=tipo_de_item_id)
            contexto['form'] = TipoDeItemForm(request.POST or None, instance=tipo_de_item)
            # TODO: mañantipoa
            # Construye un diccionario a partir de la lista de atributos

            atributos_dinamicos = recolectar_atributos(tipo_de_item)
            print(atributos_dinamicos)
            atributos_forms = atributo_form_handler(atributos_dinamicos)
            print(atributos_forms)
            contexto['atributos_seleccionados'] = atributos_forms
    return render(request, 'gestion_de_tipo_de_item/editar_tipo_de_item.html', context=contexto)
