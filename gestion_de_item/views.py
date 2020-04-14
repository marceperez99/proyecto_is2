from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from gestion_de_item.models import Item, EstadoDeItem, AtributoItemFecha, AtributoItemCadena, AtributoItemNumerico, \
    AtributoItemArchivo, AtributoItemBooleano
from gestion_de_proyecto.models import Proyecto
from gestion_de_tipo_de_item.utils import get_dict_tipo_de_item
from roles_de_proyecto.decorators import pp_requerido_en_fase
from gestion_de_fase.models import Fase
from gestion_de_tipo_de_item.models import TipoDeItem, AtributoBinario, AtributoCadena, AtributoNumerico, AtributoFecha, \
    AtributoBooleano
from .forms import RelacionPadreHijoForm, NuevoVersionItemForm, EditarItemForm, AtributoItemArchivoForm, \
    AtributoItemNumericoForm, AtributoItemCadenaForm, AtributoItemBooleanoForm, AtributoItemFechaForm
from .utils import get_atributos_forms


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pu_f_ver_fase')
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
                        assert anterior.get_fase() == fase.fase_anterior or anterior.get_fase() == fase, "El sistema " \
                                                                                                         "es inconsistente: El item anterior no peretence a esta fase ni a la fase anterior "
                        # Se decide si es un padre o un antecesor del item.
                        if anterior.get_fase() == fase.fase_anterior:
                            version.antecesores.add(anterior)
                        elif anterior.get_fase() == fase:
                            version.padres.add(anterior)

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
                        atributo.valor = form.cleaned_data[form.nombre]

                        atributo.save()

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
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        item.eliminar()

        return redirect('listar_items', proyecto_id, fase_id)

    contexto = {'item': item.version.nombre}
    return render(request, 'gestion_de_item/eliminar_item.html', context=contexto)


def ver_historial_item_view(request, proyecto_id, fase_id, item_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    contexto = {
        'item': item,
        'user': request.user,
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


def relacionar_item_view(request, proyecto_id, fase_id, item_id):
    # TODO comentar
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
                pass  # TODO hacer cuando haya la funcionalidad de Linea Base
    else:
        if 'tipo' in request.GET.keys():
            if request.GET['tipo'] == 'padre-hijo':
                contexto['form'] = RelacionPadreHijoForm(item=item)
            elif request.GET['tipo'] == 'antecesor-sucesor':
                pass  # TODO hacer cuando haya la funcionalidad de Linea Base

    return render(request, 'gestion_de_item/relacionar_item.html', contexto)



@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_aprobar_item')
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
        if item.estado == EstadoDeItem.NO_APROBADO:
            item.solicitar_aprobacion()
        return redirect('visualizar_item', proyecto.id, fase.id, item.id)

    contexto = {'proyecto': proyecto, 'fase': fase, 'item': item}
    return render(request, 'gestion_de_item/solicitar_aprobacion.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_aprobar_item')
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
        if item.estado == EstadoDeItem.A_APROBAR:
            item.aprobar()
        return redirect('visualizar_item', proyecto.id, fase.id, item.id)

    contexto = {'proyecto': proyecto, 'fase': fase, 'item': item}
    return render(request, 'gestion_de_item/aprobar_item.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_editar_item')
def editar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite editar un los atributos de un ítem. Cualquier modificación del item generara una nueva versión de este.

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
        elif type(atributo) == AtributoItemBooleano: \
                atributos_forms.append(
                    AtributoItemBooleanoForm(request.POST, plantilla=atributo.plantilla, counter=counter,
                                             initial={'valor_' + str(counter): atributo.valor}))
        elif type(atributo) == AtributoItemFecha:
            atributos_forms.append(
                AtributoItemFechaForm(request.POST, plantilla=atributo.plantilla, counter=counter,
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
                counter = 0
                for form, atributo in zip(atributos_forms, atributos_dinamicos):
                    counter = counter + 1
                    atributo.version = version
                    atributo.valor = form.cleaned_data['valor_' + str(counter)]
                    atributo.pk = None
                    atributo.save()
                # Finaliza el proceso de editar
                item.save()
                return redirect('visualizar_item', proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id)
    # En caso de que un form este mal o no sea un POST
    if not all_valid:
        contexto = {'user': request.user, 'proyecto': proyecto, 'fase': fase, 'item': item,
                    'version_actual': version_actual, 'atributos_forms': atributos_forms, 'form_version': form_version}
        return render(request, 'gestion_de_item/editar_item.html', context=contexto)
