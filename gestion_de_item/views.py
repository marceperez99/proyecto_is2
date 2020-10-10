from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from gestion_de_item.tasks import notificar_solicitud_aprobacion_item
from gestion_de_fase.decorators import fase_abierta
from gestion_de_fase.models import Fase
from gestion_de_item.models import *
from gestion_de_proyecto.decorators import estado_proyecto
from gestion_de_proyecto.models import Proyecto, EstadoDeProyecto
from gestion_de_tipo_de_item.models import *
from gestion_de_tipo_de_item.utils import get_dict_tipo_de_item
from gestion_linea_base.models import *
from roles_de_proyecto.decorators import pp_requerido_en_fase
from .decorators import estado_item

from .forms import *
from .tasks import upload_and_save_file_item
from .utils import get_atributos_forms, trazar_item


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pu_f_ver_fase')
@estado_proyecto(EstadoDeProyecto.INICIADO, EstadoDeProyecto.CANCELADO, EstadoDeProyecto.FINALIZADO)
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

    se_puede_crear = fase.fase_anterior is None or LineaBase.objects.filter(fase=fase.fase_anterior,
                                                                            estado=EstadoLineaBase.CERRADA).exists()
    se_puede_crear = se_puede_crear or Item.objects.filter(tipo_de_item__fase=fase,
                                                           estado=EstadoDeItem.APROBADO).exists() or Item.objects.filter(
        tipo_de_item__fase=fase, estado=EstadoDeItem.EN_LINEA_BASE).exists()

    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'items': items,
        'se_puede_crear': se_puede_crear,
        'permisos': participante.get_permisos_por_fase_list(fase) + participante.get_permisos_de_proyecto_list(),
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
def listar_items_en_revision(request, proyecto_id, fase_id):
    """
    Vista que permite la visualizacion de los items en estado EN REVISION, creados dentro de la fase.
    Si el usuario cuenta con el permiso de proyecto

    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    participante = proyecto.get_participante(request.user)
    items = fase.get_items(en_revision=True)
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'items': items,
        'permisos': participante.get_permisos_por_fase_list(fase) + participante.get_permisos_de_proyecto_list(),
        'breadcrumb': {'pagina_actual': 'Items en Revisión',
                       'permisos': participante.get_permisos_por_fase_list(fase),
                       'links': [
                           {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                           {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                           {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))}
                       ]
                       }
    }
    return render(request, 'gestion_de_item/listar_items_en_revision.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pu_f_ver_fase')
@estado_proyecto(EstadoDeProyecto.INICIADO, EstadoDeProyecto.CANCELADO, EstadoDeProyecto.FINALIZADO)
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
    usuario = request.user
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    participante = proyecto.get_participante(request.user)
    contexto = {
        'debe_ser_revisado': item.estado == EstadoDeItem.EN_REVISION and proyecto.tiene_permiso_de_proyecto_en_fase(
            usuario, fase, 'pp_f_decidir_sobre_items_en_revision'),
        'se_puede_eliminar': item.estado == EstadoDeItem.NO_APROBADO and
                             participante.tiene_pp_en_fase(fase, 'pp_f_eliminar_item'),
        "puede_pedir_modificacion": item.estado == EstadoDeItem.NO_APROBADO and
                                    participante.tiene_pp_en_fase(fase, 'pp_f_solicitar_aprobacion_item'),

        "puede_aprobar": item.estado == EstadoDeItem.A_APROBAR and
                         participante.tiene_pp_en_fase(fase, 'pp_f_aprobar_item'),
        "puede_desaprobar": item.estado == EstadoDeItem.APROBADO and
                            participante.tiene_pp_en_fase(fase, 'pp_f_desaprobar_item') and item.estado_anterior != EstadoDeItem.EN_LINEA_BASE,
        'puede_modificar': item.puede_modificar(proyecto.get_participante(request.user)),
        'puede_terminar_aprobacion': item.estado == EstadoDeItem.A_MODIFICAR and item.puede_modificar(
            proyecto.get_participante(request.user)),
        'proyecto': proyecto,
        'fase': fase,
        'item': item,
        'linea_base': item.get_linea_base() if item.estado == EstadoDeItem.EN_LINEA_BASE else "",
        'cambios': True,
        'trazabilidad': trazar_item(proyecto, item),
        'impacto': item.calcular_impacto(),
        'permisos': participante.get_permisos_de_proyecto_list() + participante.get_permisos_por_fase_list(fase),
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
@fase_abierta()
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
        contexto = {'user': request.user, 'lista_tipo_de_item': lista_tipo_de_item, 'fase': fase, 'proyecto': proyecto,
                    'breadcrumb': {'pagina_actual': 'Nuevo Item',
                                   'links': [
                                       {'nombre': proyecto.nombre,
                                        'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                       {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                       {'nombre': fase.nombre,
                                        'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                       {'nombre': 'Items', 'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                   ]
                                   }
                    }
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
                    version.version = 1
                    version.save()
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
                            item.add_antecesor(anterior, versionar=False)
                        elif anterior.get_fase() == fase:
                            item.add_padre(anterior, versionar=False)

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
                        # Comentar linea de abajo para que la subida de archivos sea asincrona
                        # upload_and_save_file_item(list_atributos_id)
                        # Comentar linea de abajo para que la subida de archivos sea sincrona
                        upload_and_save_file_item.delay(list_atributos_id)

                    return redirect('listar_items', proyecto_id=proyecto_id, fase_id=fase_id)

        # Si uno de los forms no fue completado correctamente.
        if not all_valid:
            form = NuevoVersionItemForm(request.POST or None, tipo_de_item=tipo_de_item)
            atributo_forms = get_atributos_forms(tipo_de_item, request)
            contexto = {'user': request.user, 'form': form, 'fase': fase, 'proyecto': proyecto,
                        'tipo_de_item': tipo_de_item, 'atributo_forms': atributo_forms,
                        'breadcrumb': {'pagina_actual': 'Nuevo Item',
                                       'links': [
                                           {'nombre': proyecto.nombre,
                                            'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                           {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                           {'nombre': fase.nombre,
                                            'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                           {'nombre': 'Items',
                                            'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                       ]
                                       }
                        }
            return render(request, 'gestion_de_item/nuevo_item.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_eliminar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.NO_APROBADO)
def eliminar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que solicita confirmación para eliminar un item.
    La eliminación consiste en cambiar el estado del item al estado ELIMINADO.
    Solo es posible eliminar un item si este se encuentra en estado No Aprobado.

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
@estado_proyecto(EstadoDeProyecto.INICIADO, EstadoDeProyecto.CANCELADO, EstadoDeProyecto.FINALIZADO)
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
    participante = proyecto.get_participante(request.user)
    contexto = {
        'item': item,
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'puede_revertirse': item.estado in [EstadoDeItem.NO_APROBADO, EstadoDeItem.A_MODIFICAR] and
                            participante.tiene_pp_en_fase(fase, "pp_f_restaurar_version"),
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
@fase_abierta()
@estado_item(EstadoDeItem.NO_APROBADO, EstadoDeItem.A_MODIFICAR)
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
                'items_aprobados': fase.get_item_estado(EstadoDeItem.APROBADO),
                'breadcrumb': {'pagina_actual': 'Relacionar Items',
                               'links': [
                                   {'nombre': proyecto.nombre,
                                    'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                   {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                   {'nombre': fase.nombre,
                                    'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                   {'nombre': 'Items', 'url': reverse('listar_items', args=(proyecto.id, fase.id))},
                                   {'nombre': item.version.nombre,
                                    'url': reverse('visualizar_item', args=(proyecto.id, fase.id, item.id))},
                               ]
                               }
                }
    if request.method == 'POST':
        if 'tipo' in request.GET.keys():
            if request.GET['tipo'] == 'padre-hijo':
                form = RelacionPadreHijoForm(request.POST, item=item)
                if form.is_valid():
                    item.add_padre(form.cleaned_data['padre'])
                    return redirect('visualizar_item', proyecto_id, fase_id, item_id)
                else:
                    contexto['form'] = form
            elif request.GET['tipo'] == 'antecesor-sucesor':
                form = RelacionAntecesorSucesorForm(request.POST, item=item)
                if form.is_valid():
                    item.add_antecesor(form.cleaned_data['antecesor'])
                    return redirect('visualizar_item', proyecto_id, fase_id, item_id)
                else:
                    contexto['form'] = form
    else:
        if 'tipo' in request.GET.keys():
            if request.GET['tipo'] == 'padre-hijo':
                contexto['form'] = RelacionPadreHijoForm(item=item)
            elif request.GET['tipo'] == 'antecesor-sucesor':
                if fase.es_primera_fase():
                    messages.error(request, "No se puede agregar un antecesor a un item de la primera fase")
                    return redirect("visualizar_item", proyecto.id, fase.id, item.id)
                else:
                    contexto['form'] = RelacionAntecesorSucesorForm(item=item)

    return render(request, 'gestion_de_item/relacionar_item.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_solicitar_aprobacion_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.NO_APROBADO)
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
            notificar_solicitud_aprobacion_item.delay(proyecto.id, fase.id, item.id, get_current_site(request).domain)
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
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.A_APROBAR, EstadoDeItem.A_MODIFICAR)
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
    tiene_permiso = proyecto.tiene_permiso_de_proyecto_en_fase(request.user, fase, "pp_f_aprobar_item")
    item_a_modificar = item.estado == EstadoDeItem.A_MODIFICAR
    item_a_aprobar = item.estado == EstadoDeItem.A_APROBAR
    usuario_encargado = item.puede_modificar(proyecto.get_participante(request.user))

    if not ((item_a_aprobar and tiene_permiso) or (item_a_modificar and usuario_encargado)):
        return redirect('sin_permiso')

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
@pp_requerido_en_fase('pp_f_modificar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.NO_APROBADO, EstadoDeItem.A_MODIFICAR)
def editar_item_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que permite editar un los atributos de un ítem. Cualquier modificación del item generara una
    nueva versión de este.

    Argumentos:
        - request: HttpRequest.\n
        - proyecto_id: int, identificador único de un  proyecto.\n
        - fase_id: int, identificador único de una fase.\n
        - item_id: int, identificador único de un item a editar.

    Retorna
        - HttpResponse
    """

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    version_actual = item.version
    if not item.puede_modificar(proyecto.get_participante(request.user)):
        return redirect('sin_permiso')
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
                padres = item.get_padres()
                antecesores = item.get_antecesores()
                version = form_version.save(commit=False)
                version.version = item.version.version + 1
                version.pk = None
                version.save()
                #

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
                    # Comentar linea de abajo para que la subida de archivos sea asincrona
                    # upload_and_save_file_item(list_atributos_id)
                    # Comentar linea de abajo para que la subida de archivos sea sincrona
                    upload_and_save_file_item.delay(list_atributos_id)

                item.save()
                for padre in padres:
                    item.add_padre(padre, versionar=False)
                for antecesor in antecesores:
                    item.add_antecesor(antecesor, versionar=False)
                # Finaliza el proceso de editar

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
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.APROBADO, EstadoDeItem.A_APROBAR)
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
        try:
            item.desaprobar()
            messages.success(request, "El item se desaprobo correctamente")
        except Exception as e:
            mensaje = '<p class="lead">El item no puede ser desaprobado debido a las siguientes razones:<br><p>'
            errores = e.args[0]

            for error in errores:
                mensaje = f"{mensaje}<li>{error}</li><br>"
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
@pp_requerido_en_fase('pp_f_eliminar_relacion_entre_items')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.A_MODIFICAR, EstadoDeItem.NO_APROBADO)
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
    fase = get_object_or_404(proyecto.fase_set
                             , id=fase_id)
    item = get_object_or_404(Item, id=item_id)
    item_relacionado = get_object_or_404(Item, id=item_relacion_id)

    if request.method == 'POST':
        try:
            item.eliminar_relacion(item_relacionado)
            messages.success(request, "La relacion se elimino correctamente")
        except Exception as e:
            mensaje = '<p class="lead">La relacion no se puede eliminar por el siguientes motivo</p>:<br><ul>'
            errores = e.args[0]
            print(errores)
            mensaje = mensaje + '<li>' + errores + '</li><br>'
            mensaje = mensaje + '</ul>'
            messages.error(request, mensaje)

        return redirect('visualizar_item', proyecto.id, fase.id, item.id)

    contexto = {'proyecto': proyecto, 'fase': fase, 'item': item}
    return render(request, 'gestion_de_item/eliminar_relacion.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_editar_item')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.NO_APROBADO, EstadoDeItem.A_MODIFICAR)
def eliminar_archivo_view(request, proyecto_id, fase_id, item_id, atributo_id):
    """
    Vista que permite elimianr un archivo de un item, creando una version del mismo sin dicho archivo

    Argumentos:
        - request: HttpRequest,
        - proyecto_id: int, identificador único de un  proyecto.
        - fase_id: int, identificador único de una fase.
        - item_id: int, identificador único de un item.
        - atributo_id int, dentificador único del atributo.

    Retorna
        - HttpResponse
    """
    atributo_archivo = get_object_or_404(AtributoItemArchivo, id=atributo_id)
    file = atributo_archivo.valor

    if request.method == 'POST':
        item = get_object_or_404(Item, id=item_id)
        item.nueva_version()

        atributo = get_object_or_404(item.version.atributoitemarchivo_set, valor=atributo_archivo.valor)
        atributo.valor = None
        atributo.save()

        return redirect('visualizar_item', proyecto_id, fase_id, item_id)

    contexto = {'file': file, }
    return render(request, 'gestion_de_item/eliminar_archivo.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_decidir_sobre_items_en_revision')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.EN_REVISION)
def debe_modificar_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que muestra dos  pantallas de confirmación para marcar un item como A modificar dependiendo de si este se encuentra en una linea base o no.

    Argumentos:
        -request: HttpRequest
        -proyecto_id: int , id del proyecto.
        -fase_id: int, id de la fase.
        -item_id: int, id del item.
    Retorna:
        -HttpResponse
    """
    item = get_object_or_404(Item, id=item_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    if request.method == 'POST':

        if not item.esta_en_linea_base():
            if item.estado_anterior == EstadoDeItem.EN_LINEA_BASE:
                #Coloca el estado del item en Aprobado
                item.estado = EstadoDeItem.APROBADO
                item.save()
            else:
                # Coloca el estado del item en A modificar.
                item.solicitar_modificacion()

            hijos = item.get_hijos()
            sucesores = item.get_sucesores()
            dependencias = list(hijos) + list(sucesores)

            for dependencia in dependencias:
                if dependencia.estado in [EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE]:
                    dependencia.solicitar_revision()

            return redirect('visualizar_item', proyecto_id, fase_id, item_id)
        else:
            linea_base = item.get_linea_base()
            return redirect('solicitar_rompimiento', proyecto_id, fase_id, linea_base.id)
    else:
        if not item.esta_en_linea_base():
            mensaje = ""
            print(item.estado_anterior)
            if item.estado_anterior == EstadoDeItem.EN_LINEA_BASE:
                mensaje = "El ítem \"" + item.version.nombre + "\" pertenecía a una línea base. Para poder modificarlo es necesaria una solicitud " \
                          "de cambio. Si confirma su decisión el ítem será puesto en el estado Aprobado y deberá ser " \
                          "incluido en una línea base para realizar la solicitud. Los ítems que dependan directamente " \
                          "de este ítem y estén aprobados o en línea base serán colocados en revisión. "
            else:

                mensaje = "El item \"" + item.version.nombre + "\" será colocado en el estado <strong>A Modificar.</strong>"
            hijos = item.get_hijos()
            sucesores = item.get_sucesores()
            dependencias = list(hijos) + list(sucesores)
            item_afectados = list(
                filter(lambda dependencia: dependencia.estado in [EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE],
                       dependencias))
            contexto = {'item': item, 'fase': fase, 'proyecto': proyecto, 'item_afectados': item_afectados,
                        'hay_items_afectados': len(item_afectados) > 0,'mensaje':mensaje}
            return render(request, 'gestion_de_item/confirmar_modificacion_no_linea_base.html', context=contexto)
        else:
            linea_base = item.get_linea_base()
            contexto = {'item': item, 'fase': fase, 'proyecto': proyecto, 'linea_base': linea_base,}
            return render(request, 'gestion_de_item/confirmar_modificacion_linea_base.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_decidir_sobre_items_en_revision')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.EN_REVISION)
def no_modificar_view(request, proyecto_id, fase_id, item_id):
    """
    Vista que muestra la pantallas de confirmación para volver al estado anterior de un item, ya que no se modificará

    Argumentos:
        -request: HttpRequest
        -proyecto_id: int , id del proyecto.
        -fase_id: int, id de la fase.
        -item_id: int, id del item.
    Retorna:
        -HttpResponse
    """
    item = get_object_or_404(Item, id=item_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    if request.method == 'POST':
        if item.esta_en_linea_base():
            item.estado = EstadoDeItem.EN_LINEA_BASE
            item.estado_anterior = ""
        else:
            item.estado = EstadoDeItem.APROBADO
            item.estado_anterior = ""
        #estadoaux = item.estado
        #item.estado = item.estado_anterior
        #item.estado_anterior = estadoaux
        item.save()

        linea_base = item.get_linea_base() if item.esta_en_linea_base() else None

        if linea_base is not None and all(item.estado == EstadoDeItem.EN_LINEA_BASE for item in linea_base.items.all()):
            linea_base.estado = EstadoLineaBase.CERRADA
            linea_base.save()

        return redirect('visualizar_item', proyecto_id, fase_id, item_id)
    else:
        contexto = {'item': item, 'fase': fase, 'proyecto': proyecto}
        return render(request, 'gestion_de_item/confirmar_no_modificacion_item.html', context=contexto)

@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_decidir_sobre_items_en_revision')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.EN_REVISION)
def terminar_revision_view(request,proyecto_id,fase_id,item_id):
    item = get_object_or_404(Item, id=item_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    mensaje = ""
    if request.method == "POST":
        #Si estaba aprobado
        if item.estado_anterior == EstadoDeItem.APROBADO:
            item.estado = EstadoDeItem.APROBADO
            item.estado_anterior = EstadoDeItem.EN_REVISION
        elif item.estado_anterior == EstadoDeItem.EN_LINEA_BASE:
            #Si se encuentra en una linea base comprometida
            if item.esta_en_linea_base():
                item.estado = EstadoDeItem.EN_LINEA_BASE
                item.estado_anterior = EstadoDeItem.EN_REVISION
            else:
            #Si se encontraba en una linea base rota.
                item.estado = EstadoDeItem.APROBADO
                item.estado_anterior = EstadoDeItem.EN_LINEA_BASE
        item.save()
        return redirect('visualizar_item',proyecto_id,fase_id,item_id)
    else:
        if item.estado_anterior == EstadoDeItem.APROBADO:
            mensaje = f"El item \"{item.version.nombre}\" será colocado en el estado APROBADO. Si se desea modificar el item debera desaprobarse."
        elif item.estado_anterior == EstadoDeItem.EN_LINEA_BASE:
            if item.esta_en_linea_base():
                mensaje = f"El item \"{item.version.nombre}\" se encuentra en una Linea Base comprometida. El item será colocado en el estado En linea Base. Si se desea modificar el item se debera realizar una solicitud de rompimiento " \
                          f"especificando los motivos para modificar este item."
            else:
                mensaje = f"El item \"{item.version.nombre}\" pertenecía a una línea base. Para poder modificarlo es necesaria una solicitud de cambio. Si confirma su decisión el ítem será puesto en el estado Aprobado y deberá ser incluido en una línea base para realizar la solicitud de rompimiento."
        contexto = {'item':item,'proyecto':proyecto,'fase':fase,'mensaje':mensaje}
        return render(request,'gestion_de_item/terminar_revision.html',context = contexto)

@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_restaurar_version')
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
@estado_item(EstadoDeItem.A_MODIFICAR, EstadoDeItem.NO_APROBADO)
def restaurar_version_item_view(request, proyecto_id, fase_id, item_id, version_id):
    """
    Vista que permite restaurar un Item a una version anterior, siempre y cuando el cambio no genere inconsistencias.
    Si el metodo Http con el que se realizo la peticion fue GET, se le mostrara al usuario todas las veriones del item,
    con lo que el usuario podra restaurar a la version que mejor le convenga.\n
    Si el metodo Http con el que se realizo la peticion fue POST, se verificara si el valido restaurar a la version
    seleccionada por el usuario, mostrando un mensaje de confirmacion o de error de acuerdoa lo que pase.\n
    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, identificador unico de un proyecto del sistema.
        - fase_id: int, identificador unico de una fase de un proyecto.
        - item_id: int, identificador unico del item.
        - version_id: int, identificador unico de la version

    Retorna:
        - request: HttpRequest
    """

    item = get_object_or_404(Item, id=item_id)
    version = get_object_or_404(VersionItem, id=version_id)
    if request.method == 'POST':
        if item.puede_restaurarse(version):
            item.restaurar(version)
            messages.success(request, "El item pudo restaurarse a una version anterior correctamente")
        else:
            messages.error(request,
                           "El item no puede restaurarse a una version anterior, pues deja de ser trazable  la primera fase")
        return redirect('visualizar_item', proyecto_id, fase_id, item_id)

    else:
        return render(request, 'gestion_de_item/restaurar_item.html')
