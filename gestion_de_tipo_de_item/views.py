from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from gestion_de_fase.models import Fase
from gestion_de_proyecto.decorators import estado_proyecto
from gestion_de_proyecto.models import Proyecto, EstadoDeProyecto
from gestion_de_tipo_de_item.forms import TipoDeItemForm, AtributoCadenaForm, AtributoArchivoForm, AtributoBooleanoForm, \
    AtributoNumericoForm, AtributoFechaForm
from gestion_de_tipo_de_item.models import TipoDeItem
from gestion_de_tipo_de_item.utils import get_dict_tipo_de_item
from gestion_de_tipo_de_item.utils import guardar_atributos, guardar_tipo_de_item, atributo_form_handler, \
    construir_atributos, recolectar_atributos
from roles_de_proyecto.decorators import pp_requerido_en_fase, pp_requerido


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pu_ver_proyecto')
def tipo_de_item_view(request, proyecto_id, fase_id, tipo_de_item_id):
    """
    Vista que permite visualizar el nombre, la descripción, y los atributos de un tipo de item

    Argumentos:
        request: HttpRequest \n
        proyecto_id: int id que identifica unicamente a un proyecto. \n
        fase_id: int id que identifica unicamente a una fase \n
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    tipo_de_item = get_object_or_404(fase.tipodeitem_set, id=tipo_de_item_id)

    contexto = {'user': request.user,
                'proyecto': proyecto,
                'fase': fase,
                'tipo_de_item': get_dict_tipo_de_item(tipo_de_item),
                'es_utilizado': tipo_de_item.es_utilizado(),
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


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido('pu_ver_proyecto')
def listar_tipo_de_item_view(request, proyecto_id, fase_id):
    """
    Vista que permite visualizar los tipos de items asociados a una fase de un proyecto.

    Argumentos:
        request: HttpRequest. \n
        proyecto_id: int id que identifica unicamente a un proyecto. \n
        fase_id: int id que identifica unicamente a una fase.

    Retorna:
        HttpResponse
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


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_crear_tipo_de_item')
@estado_proyecto(EstadoDeProyecto.CONFIGURACION, EstadoDeProyecto.INICIADO)
def nuevo_tipo_de_item_view(request, proyecto_id, fase_id, tipo_de_item_id=None):
    """
    Vista que muestra la pantalla de creación de un nuevo tipo de item.\n
    Se habilita la opción de importar tipo de item a los usuarios con permiso de proyecto importar tipo de item.
    Permite agregar nuevos atributos al tipo de item.

    Argumentos:
        request: HttpRequest \n
        proyecto_id: int id que identica unicamente a un proyecto del sistema. \n
        fase_id: int id que identifica unicamente a una fase del sistema. \n
        tipo_de_item: int id que identifica unicamente una tipo de item. (solo si se esta importando un tipo de item)

    Retorna:
        HttpReponse
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
        atributos_dinamicos = construir_atributos(request)
        atributos_forms = atributo_form_handler(atributos_dinamicos)

        tipo_de_item_form = TipoDeItemForm(request.POST or None, proyecto=proyecto)
        if tipo_de_item_form.is_valid():
            tipo_de_item = tipo_de_item_form.save(commit=False)

            all_valid = True
            # Se validan todos los forms
            for form in atributos_forms:
                all_valid = all_valid and form.is_valid()

            if all_valid:

                guardar_tipo_de_item(tipo_de_item, fase, request.user)
                guardar_atributos(atributos_forms, tipo_de_item)

                return redirect('tipos_de_item', proyecto_id=proyecto_id, fase_id=fase_id)
            else:
                contexto['form'] = tipo_de_item_form
                contexto['atributos_seleccionados'] = atributos_forms
        else:
            contexto['form'] = tipo_de_item_form
            contexto['atributos_seleccionados'] = atributos_forms
    else:
        if tipo_de_item_id is None:
            contexto['form'] = TipoDeItemForm(proyecto=proyecto)
        else:
            tipo_de_item = get_object_or_404(TipoDeItem, id=tipo_de_item_id)
            contexto['form'] = TipoDeItemForm(request.POST or None, proyecto=proyecto, instance=tipo_de_item)
            # Construye un diccionario a partir de la lista de atributos
            atributos_dinamicos = recolectar_atributos(tipo_de_item)
            atributos_forms = atributo_form_handler(atributos_dinamicos)
            contexto['atributos_seleccionados'] = atributos_forms
    return render(request, 'gestion_de_tipo_de_item/nuevo_tipo_de_item.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase("pp_f_importar_tipo_de_item")
@estado_proyecto(EstadoDeProyecto.CONFIGURACION, EstadoDeProyecto.INICIADO)
def importar_tipo_de_item_view(request, proyecto_id, fase_id):
    """
    Vista que permite seleccionar un tipo de item del sistema para copiar sus atributos a un nuevo tipo de item para
    su modificación y creación.

    Argumentos:
        request: HttpRequest. \n
        proyecto_id: int id que identifica unicamente a un proyecto del sistema. \n
        fase_id: int id que identifica unicamente a una fase del sistema.

    Retorna:
        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    fase = get_object_or_404(Fase, pk=fase_id)
    # Lista de diccionarios de tipo de item
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


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_editar_tipo_de_item')
@estado_proyecto(EstadoDeProyecto.CONFIGURACION, EstadoDeProyecto.INICIADO)
def editar_tipo_de_item_view(request, proyecto_id, fase_id, tipo_de_item_id):
    """
    Vista que permite editar un tipo de item.
    Si el metodo Http con el que se realizo la peticion fue GET, muestra al usuario los campos ya cargados del tipo de
    item, con la opcion de editarlos.
    Si el metodo Http con el que se realizo la peticion fue POST, elimina el viejo tipo de item, y crea uno nuevo
    en base a los datos recibidos.
    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - tipo_de_item_id: int, identificador unico del tipo de item.

    Retorna:
        - request: HttpRequest
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
        tipo_de_item_form = TipoDeItemForm(request.POST or None, proyecto=proyecto, tipo_de_item=tipo_de_item)
        atributos_dinamicos = construir_atributos(request)
        atributos_forms = atributo_form_handler(atributos_dinamicos)
        if tipo_de_item_form.is_valid():
            tipo_de_item = tipo_de_item_form.save(commit=False)

            all_valid = True
            # Se validan todos los forms
            for form in atributos_forms:
                all_valid = all_valid and form.is_valid()

            if all_valid:

                guardar_tipo_de_item(tipo_de_item, fase, request.user)
                guardar_atributos(atributos_forms, tipo_de_item)
                tipo_de_item = TipoDeItem.objects.get(id=tipo_de_item_id)
                tipo_de_item.delete()

                return redirect('tipos_de_item', proyecto_id=proyecto_id, fase_id=fase_id)
            else:
                contexto['form'] = tipo_de_item_form
                contexto['atributos_seleccionados'] = atributos_forms
        else:
            contexto['form'] = tipo_de_item_form
            contexto['atributos_seleccionados'] = atributos_forms

    else:
        if tipo_de_item_id is None:
            contexto['form'] = TipoDeItemForm(proyecto=proyecto)
        else:
            tipo_de_item = get_object_or_404(TipoDeItem, id=tipo_de_item_id)
            contexto['form'] = TipoDeItemForm(request.POST or None, proyecto=proyecto, instance=tipo_de_item)

            # Construye un diccionario a partir de la lista de atributos

            atributos_dinamicos = recolectar_atributos(tipo_de_item)
            atributos_forms = atributo_form_handler(atributos_dinamicos)
            contexto['atributos_seleccionados'] = atributos_forms
    return render(request, 'gestion_de_tipo_de_item/editar_tipo_de_item.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_eliminar_tipo_de_item')
@estado_proyecto(EstadoDeProyecto.CONFIGURACION, EstadoDeProyecto.INICIADO)
def eliminar_tipo_de_item_view(request, proyecto_id, fase_id, tipo_de_item_id):
    """
    Vista que se encarga de, si ningun item de ese tipo, eliminar el tipo de item recibido

    Argumentos:
        request: HttpRequest. \n
        proyecto_id: int id que identifica unicamente a un proyecto del sistema. \n
        fase_id: int id que identifica unicamente a una fase del sistema.\m
        tipo_de_item_id: int id que identifica unicamente al tipo de item

    Retorna:
        HttpResponse
    """

    tipo_de_item = get_object_or_404(TipoDeItem, id=tipo_de_item_id)

    if request.method == 'POST':
        # pasar mensaje
        if not tipo_de_item.es_utilizado():
            tipo_de_item.delete()

        return redirect('tipos_de_item', proyecto_id, fase_id)
    contexto = {'tipo_de_item': tipo_de_item.nombre}
    return render(request, 'gestion_de_tipo_de_item/eliminar_tipo_de_item.html', context=contexto)
