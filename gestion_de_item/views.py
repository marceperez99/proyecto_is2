from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from gestion_de_fase.models import Fase
from gestion_de_item.models import Item, EstadoDeItem, AtributoItemFecha, AtributoItemCadena, AtributoItemNumerico, \
    AtributoItemArchivo, AtributoItemBooleano
from gestion_de_proyecto.decorators import estado_proyecto
from gestion_de_proyecto.models import Proyecto, EstadoDeProyecto
from gestion_de_tipo_de_item.models import TipoDeItem, AtributoBinario, AtributoCadena, AtributoNumerico, AtributoFecha, \
    AtributoBooleano
from gestion_de_tipo_de_item.utils import get_dict_tipo_de_item
from roles_de_proyecto.decorators import pp_requerido_en_fase
from .forms import RelacionPadreHijoForm, RelacionAntecesorSucesorForm, NuevoVersionItemForm, EditarItemForm, \
    AtributoItemArchivoForm, \
    AtributoItemNumericoForm, AtributoItemCadenaForm, AtributoItemBooleanoForm, AtributoItemFechaForm
from .tasks import upload_and_save_file_item
from .utils import get_atributos_forms  # , upload_and_save_file_item


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pu_f_ver_fase')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def listar_items(request, proyecto_id, fase_id):
    """
    Vista que permite la visualizacion de los items creados dentro de la fase.
    Si el usuario cuenta con el permiso de proyecto

    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    participante = proyecto.get_participante(request.user)
    if participante.tiene_pp_en_fase(fase, 'pp_f_ver_items_eliminados'):
        items = fase.get_items(items_eliminados=True)
    else:
        items = fase.get_items()
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'items': items,
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
@pp_requerido_en_fase('pu_f_ver_fase')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def visualizar_item(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite la visualizacion de la informacion de un Item, en esta vista se presentan las opciones
    de Modificar Item, Aprobar Item, Eliminar Item.

    Argumentos:
        request: HttpRequest.\n
        proyecto_id:(int) identificador unico del proyecto al que se esta accediendo.\n
        fase_id:(int) identificador unico de la fase del proyecto donde esta el item.\n
        item_id:(int) identificador unico del item que se desea visualizar.

    Retorna:
        HttpResponse

    Requiere permisos de Proyecto:
        pu_f_ver_fase: Visualizar Fase de Proyecto
    """

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    contexto = {
        'se_puede_eliminar': item.estado == EstadoDeItem.NO_APROBADO,
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


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_crear_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def nuevo_item_view(request, proyecto_id, fase_id, tipo_de_item_id=None, item=None):
    """
    Viste que permite la creación de un nuevo item despues de seleccionar el tipo de item al que corresponde.
    Si la vista es llamada sin tipo_de_item_id como argumento permite seleccionar un tipo de item de la fase.

    Argumentos:
        - request : HttpRequest
        - proyecto_id : int , identificador único de un proyecto.
        - fase_id: int, identificador único de una fase.
        - tipo_de_item_id: int, identificador del tipo de item seleccionado
    Retorna:
        - HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)

    # Si es llamado sin tipo_de_item, permite seleccionar uno
    if tipo_de_item_id is None:

        lista_tipo_de_item = [get_dict_tipo_de_item(tipo) for tipo in TipoDeItem.objects.filter(fase=fase)]
        contexto = {'user': request.user, 'lista_tipo_de_item': lista_tipo_de_item, 'fase': fase, 'proyecto': proyecto}
        return render(request, 'gestion_de_item/seleccionar_tipo_de_item.html', context=contexto)
    else:
        # Si es llamado con un tipo de item, permite crear un nuevo tipo de item.
        tipo_de_item = get_object_or_404(TipoDeItem, id=tipo_de_item_id)
        all_valid = False
        if request.method == 'POST':

            form_nuevo = NuevoVersionItemForm(request.POST or None, tipo_de_item=tipo_de_item)

            # Consigue los atributos asociados al tipo de item.
            atributo_forms = get_atributos_forms(tipo_de_item, request)

            # Si el form de version es valido
            if form_nuevo.is_valid():

                version = form_nuevo.save(commit=False)
                # Se consigue el item a relacionar con este nuevo item.
                anterior = form_nuevo.cleaned_data['relacion']

                all_valid = True
                # Se validan todos los forms de los atributos dinamicos.
                for form in atributo_forms:
                    all_valid = all_valid and form.is_valid()

                if all_valid:

                    if item is None:  # Legacy condition, ignore.
                        # Crea un item.
                        item = Item(tipo_de_item=tipo_de_item)
                        item.estado = EstadoDeItem.NO_APROBADO
                        item.codigo = item.tipo_de_item.prefijo + '_' + str(
                            item.tipo_de_item.item_set.all().count() + 1)
                        item.save()

                    # Asocia esta versión al item creado.
                    version.item = item
                    version.save(versionar=True)
                    # Actualiza la version del item a esta versión creada.
                    item.version = version
                    item.save()

                    # Si se seleccionó un item a relacionar
                    if anterior is not None:
                        assert anterior.get_fase() == fase.fase_anterior or \
                               anterior.get_fase() == fase, "El sistema es inconsistente: El item anterior no " \
                                                            "peretence a esta fase ni a la fase anterior "
                        # Se decide si es un padre o un antecesor del item.
                        if anterior.get_fase() == fase.fase_anterior:
                            item.add_antecesor(anterior)
                        elif anterior.get_fase() == fase:
                            item.add_padre(anterior)

                    list_atributos_id = []
                    # Crea los atributos dinamicos del item.
                    for form in atributo_forms:
                        if type(form.plantilla) == AtributoCadena:
                            atributo = AtributoItemCadena()
                        elif type(form.plantilla) == AtributoNumerico:
                            atributo = AtributoItemNumerico()
                        elif type(form.plantilla) == AtributoBinario:
                            atributo = AtributoItemArchivo()
                        elif type(form.plantilla) == AtributoFecha:
                            atributo = AtributoItemFecha()
                        elif type(form.plantilla) == AtributoBooleano:
                            atributo = AtributoItemBooleano()

                        # Asocia al atributo el tipo de item y la plantilla del atributo.
                        atributo.plantilla = form.plantilla
                        atributo.version = version

                        if type(atributo) == AtributoItemArchivo and form.cleaned_data[form.nombre] is not None:
                            atributo.archivo_temporal = request.FILES[form.nombre]
                            atributo.save()
                            list_atributos_id.append(atributo.id)
                            # list_files.append(request.FILES[form.nombre])
                        else:
                            atributo.valor = form.cleaned_data[form.nombre]
                            atributo.save()

                    if len(list_atributos_id) > 0:
                        # gd_storage = GoogleDriveStorage()
                        upload_and_save_file_item(list_atributos_id)

                    return redirect('listar_items', proyecto_id=proyecto_id, fase_id=fase_id)

        # Si uno de los forms no fue completado correctamente.
        if not all_valid:
            form = NuevoVersionItemForm(request.POST or None, tipo_de_item=tipo_de_item)
            atributo_forms = get_atributos_forms(tipo_de_item, request)
            contexto = {'user': request.user, 'form': form, 'fase': fase, 'proyecto': proyecto,
                        'tipo_de_item': tipo_de_item, 'atributo_forms': atributo_forms}
            return render(request, 'gestion_de_item/nuevo_item.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_eliminar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def eliminar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que solicita confirmación para eliminar un item.
    La eliminación consiste en cambiar el estado del item al estado ELIMINADO.
    Solo es posible eliminar un item si este se encuentra en estado CREADO.

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - item_id: int, identificador unico del item a eliminar.

    Retorna:
        - HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        try:
            item.eliminar()
        except Exception as e:
            mensaje = 'El item no puede ser eliminado debido a las siguientes razones:<br>'

            errores = e.args[0]

            for error in errores:
                mensaje = mensaje + '<li>' + error + '</li><br>'
            mensaje = '<ul>' + mensaje + '</ul>'
            messages.error(request, mensaje)
            return redirect('visualizar_item', proyecto_id, fase_id, item_id)
        return redirect('listar_items', proyecto_id, fase_id)

    contexto = {'item': item.version.nombre,
                'breadcrumb': {'pagina_actual': 'Desaprobar Item',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Items',
                                          'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                         {'nombre': item,
                                          'url': reverse('visualizar_item', args=(proyecto.id, fase.id, item.id))}
                                         ]
                               }
                }
    return render(request, 'gestion_de_item/eliminar_item.html', context=contexto)


@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_ver_historial_de_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def ver_historial_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite la visualizacion del Historial de Cambios de un Item.

    Argumentos:
        request: HttpRequest, petición recibida por el servidor.\n
        proyecto_id: int, identificador único del proyecto.\n
        fase_id: int, identificador único de la fase del proyecto.\n
        item_id: int, identificador único del item dentro de la fase.

    Retorna:
        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    contexto = {
        'item': item,
        'user': request.user,
        'lista_estados_item': [EstadoDeItem.NO_APROBADO, ],
        'breadcrumb': {'pagina_actual': 'Historial de Cambios',
                       'links': [
                           {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                           {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                           {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                           {'nombre': 'Items', 'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                           {'nombre': item.version.nombre,
                            'url': reverse('visualizar_item', args=(proyecto.id, fase.id, item.id))},
                       ]
                       }
    }
    return render(request, 'gestion_de_item/historial_item.html', contexto)


@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_relacionar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def relacionar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite relacionar dos item de una misma fase (padre-hijo) o de
    fases adyacentes (antecesor-sucesor), de acuerdo a la opcion que elija el usuario se mostraran
    los item aprobados de la misma fase o de la fase adyacente para ser relacionados
    Si el metodo Http con el que se realizo la peticion fue GET, se traer todos los item aprobados,
    de esa fase o de la adyacente \n
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos de la relacion,
    verifica si es valido y la guarda \n
    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - item_id: int, identificador unico del item.
    Retorna
        - request: HttpRequest
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    contexto = {'proyecto': proyecto,
                'fase': fase,
                'item': item,
                'items_aprobados': fase.get_item_estado(EstadoDeItem.APROBADO)
                }
    if request.method == 'POST':
        if 'tipo' in request.GET.keys():
            if request.GET['tipo'] == 'padre-hijo':
                form = RelacionPadreHijoForm(request.POST, item=item)
                if form.is_valid():
                    item.add_padre(form.cleaned_data['padre'])
                else:
                    contexto['form'] = form
            elif request.GET['tipo'] == 'antecesor-sucesor':
                form = RelacionAntecesorSucesorForm(request.POST, item=item)
                if form.is_valid():
                    item.add_antecesor(form.cleaned_data['antecesor'])
                else:
                    contexto['form'] = form
        return redirect('visualizar_item', proyecto_id, fase_id, item_id)
    else:
        if 'tipo' in request.GET.keys():
            if request.GET['tipo'] == 'padre-hijo':
                contexto['form'] = RelacionPadreHijoForm(item=item)
            elif request.GET['tipo'] == 'antecesor-sucesor':
                contexto['form'] = RelacionAntecesorSucesorForm(item=item)

    return render(request, 'gestion_de_item/relacionar_item.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_aprobar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def solicitar_aprobacion_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite solicitar la aprobacion de un item que se encuentre en el estado No Aprobado.
    La aprobación del item deberá ser realizada por un participante del proyecto con el permiso de
    'Aprobar Item' dentro de la fase donde se encuentra el item.

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - item_id: int, identificador unico del item a eliminar.

    Retorna:
        - HttpResponse

    Requiere:
        - 'pp_f_aprobar_item': permiso de proyecto para aprobar item.
    """

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        try:
            item.solicitar_aprobacion()
            messages.success(request, 'Se ha solicitado la aprobacion del Item correctamente.')
        except Exception as e:
            messages.error(request, e)

        return redirect('visualizar_item', proyecto.id, fase.id, item.id)

    contexto = {'proyecto': proyecto, 'fase': fase, 'item': item,
                'breadcrumb': {'pagina_actual': 'Solicitar Aprobación Item',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Items',
                                          'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                         {'nombre': item,
                                          'url': reverse('visualizar_item', args=(proyecto.id, fase.id, item.id))}
                                         ]
                               }
                }
    return render(request, 'gestion_de_item/solicitar_aprobacion.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_aprobar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def aprobar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite la aprobacion de un item que ha sido puesto en el estado A Aprobar.

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - item_id: int, identificador unico del item a eliminar.

    Retorna:
        - HttpResponse
    """

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        try:
            item.aprobar()
            messages.success(request, 'Se ha aprobado el Item correctamente.')
        except Exception as e:
            messages.error(request, e)

        return redirect('visualizar_item', proyecto.id, fase.id, item.id)

    contexto = {'proyecto': proyecto, 'fase': fase, 'item': item,
                'breadcrumb': {'pagina_actual': 'Aprobar Item',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Items',
                                          'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                         {'nombre': item,
                                          'url': reverse('visualizar_item', args=(proyecto.id, fase.id, item.id))}
                                         ]
                               }
                }
    return render(request, 'gestion_de_item/aprobar_item.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_editar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def editar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite editar un los atributos de un ítem. Cualquier modificación del item generara una
    nueva versión de este.

    Argumentos:
        - request: HttpRequest,
        - proyecto_id: int, identificador único de un  proyecto.
        - fase_id: int, identificador único de una fase.
        - item_id: int, identificador único de un item a editar.

    Retorna
        - HttpResponse
    """

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    version_actual = item.version

    # Carga todos los formularios

    form_version = EditarItemForm(request.POST or None, instance=version_actual)
    # Consigue todos los atributos de este item.
    atributos_dinamicos = item.get_atributos_dinamicos()
    atributos_forms = []
    counter = 0
    # Crea un form para cada atributo
    for atributo in atributos_dinamicos:
        counter = counter + 1
        if type(atributo) == AtributoItemCadena:
            atributos_forms.append(
                AtributoItemCadenaForm(request.POST or None, plantilla=atributo.plantilla, counter=counter,
                                       initial={'valor_' + str(counter): atributo.valor}))
        elif type(atributo) == AtributoItemNumerico:
            atributos_forms.append(
                AtributoItemNumericoForm(request.POST or None, plantilla=atributo.plantilla, counter=counter,
                                         initial={'valor_' + str(counter): atributo.valor.normalize()}))
        elif type(atributo) == AtributoItemArchivo:
            atributos_forms.append(
                AtributoItemArchivoForm(request.POST or None, request.FILES, plantilla=atributo.plantilla,
                                        counter=counter, initial={'valor_' + str(counter): atributo.valor}))
        elif type(atributo) == AtributoItemBooleano:
            atributos_forms.append(AtributoItemBooleanoForm(request.POST, plantilla=atributo.plantilla, counter=counter,
                                                            initial={'valor_' + str(counter): atributo.valor}))
        elif type(atributo) == AtributoItemFecha:
            atributos_forms.append(
                AtributoItemFechaForm(request.POST, plantilla=atributo.plantilla,
                                      fecha=atributo.valor, counter=counter,
                                      initial={'valor_' + str(counter): atributo.valor}))

    all_valid = False
    if request.method == 'POST':
        # Verifica si los atributos estaticos son validos.
        if form_version.is_valid():
            all_valid = True
            # Verifica si los atributos dinamicos son validos.
            for form in atributos_forms:
                all_valid = all_valid and form.is_valid()

            # Si todos los formularios son validos
            if all_valid:
                version = form_version.save()
                # Relaciona el item a esta version
                item.version = version

                # Crea nuevos atributos dinamicos relacionados a esta nueva version
                list_atributos_id = []
                counter = 0
                for form, atributo in zip(atributos_forms, atributos_dinamicos):
                    counter = counter + 1
                    atributo.version = version

                    atributo.pk = None
                    for key in request.FILES.keys():
                        print("key: " + key)
                    if form.nombre in request.FILES.keys():
                        print('form.nombre: ' + form.nombre)
                        print(request.FILES[form.nombre])
                        atributo.archivo_temporal = request.FILES[form.nombre]
                        atributo.save()
                        list_atributos_id.append(atributo.id)
                    else:
                        atributo.valor = form.cleaned_data["valor_" + str(counter)]
                        atributo.save()

                if len(list_atributos_id) > 0:
                    # gd_storage = GoogleDriveStorage()
                    upload_and_save_file_item(list_atributos_id)

                # Finaliza el proceso de editar
                item.save()
                return redirect('visualizar_item', proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id)
    # En caso de que un form este mal o no sea un POST
    if not all_valid:
        contexto = {'user': request.user, 'proyecto': proyecto, 'fase': fase, 'item': item,
                    'version_actual': version_actual, 'atributos_forms': atributos_forms, 'form_version': form_version,
                    'breadcrumb': {'pagina_actual': 'Modificar Item',
                                   'links': [{'nombre': proyecto.nombre,
                                              'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                             {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                             {'nombre': fase.nombre,
                                              'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                             {'nombre': 'Items',
                                              'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                             {'nombre': item,
                                              'url': reverse('visualizar_item', args=(proyecto.id, fase.id, item.id))}
                                             ]
                                   }
                    }
        return render(request, 'gestion_de_item/editar_item.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_desaprobar_item')
def desaprobar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite la desaprobacion de un item, esta cambia su estado de Aprobado a No Aprobado.
    Si no es porsible cambiar el estado a No Aprobado, se muestra una lista de las razones por las
    cuales no se puede cambiar el estado.\n
    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - item_id: int, identificador unico del item a desaprobar.

    Retorna:
        - HttpResponse
    """

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        if item.estado == EstadoDeItem.APROBADO:
            try:
                item.desaprobar()
                messages.success(request, "El item se desaprobo correctamente")
            except Exception as e:
                mensaje = 'El item no puede ser desaprobado debido a las siguientes razones:<br>'
                errores = e.args[0]
                for error in errores:
                    mensaje = mensaje + '<li>' + error + '</li><br>'
                mensaje = '<ul>' + mensaje + '</ul>'
                messages.error(request, mensaje)

        return redirect('visualizar_item', proyecto.id, fase.id, item.id)

    contexto = {'proyecto': proyecto, 'fase': fase, 'item': item,
                'breadcrumb': {'pagina_actual': 'Desaprobar Item',
                               'links': [{'nombre': proyecto.nombre,
                                          'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                         {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                         {'nombre': fase.nombre,
                                          'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                         {'nombre': 'Items',
                                          'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                         {'nombre': item,
                                          'url': reverse('visualizar_item', args=(proyecto.id, fase.id, item.id))}
                                         ]
                               }
                }

    return render(request, 'gestion_de_item/desaprobar_item.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_desaprobar_item')
def eliminar_relacion_item_view(request, proyecto_id, fase_id, item_id, item_relacion_id):
    """
    Vista que permite eliminar la relacion de dos item de una misma fase (padre-hijo) o de
    fases adyacentes (antecesor-sucesor).
    Si el metodo Http con el que se realizo la peticion fue GET, le pide al usuario que confirme la eliminacion de la ralacion\n
    Si el metodo Http con el que se realizo la peticion fue POST, se verifica que todos los item sean trazables a la primera fase
    antes de eliminar la realcion, se muestra un mensaje si no se puede eliminar la relacion\n
    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - item_id: int, identificador unico del item.
        - item_relacion_id: int, identificador unico del item

    Retorna:
        - request: HttpRequest
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    item_relacionado = get_object_or_404(Item, id=item_relacion_id)

    if request.method == 'POST':
        try:
            item.eliminar_relacion(item_relacionado)
            messages.success(request, "La relacion se elimino correctamente")
        except Exception as e:
            mensaje = 'La relacion no se puede eliminar por los siguientes motivos<br><ul>'
            errores = e.args[0]
            for error in errores:
                mensaje = mensaje + '<li>' + error + '</li><br>'
            mensaje = mensaje + '</ul>'
            messages.error(request, mensaje)

        return redirect('visualizar_item', proyecto.id, fase.id, item.id)

    contexto = {'proyecto': proyecto, 'fase': fase, 'item': item}
    return render(request, 'gestion_de_item/eliminar_relacion.html', contexto)
