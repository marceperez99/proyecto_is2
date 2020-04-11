from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse

from gestion_de_item.models import Item, EstadoDeItem
from gestion_de_proyecto.models import Proyecto
from gestion_de_tipo_de_item.utils import get_dict_tipo_de_item
from roles_de_proyecto.decorators import pp_requerido_en_fase
from gestion_de_fase.models import Fase
from gestion_de_tipo_de_item.models import TipoDeItem, AtributoBinario, AtributoCadena, AtributoNumerico, AtributoFecha, \
    AtributoBooleano
from .forms import *
from .utils import *


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pu_f_ver_fase')
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
        'se_puede_eliminar': item.estado == EstadoDeItem.CREADO,
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
            atributo_forms = get_atributos_forms(tipo_de_item,request)

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
                        item = Item()
                        item.tipo_de_item = tipo_de_item
                        item.estado = EstadoDeItem.CREADO
                        item.codigo = tipo_de_item.prefijo + '_' + str(tipo_de_item.item_set.all().count() + 1)
                        item.save()

                    # Asocia esta versión al item creado.
                    version.version = item.version_item.all().count() + 1
                    version.item = item
                    version.save()
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
            atributo_forms = get_atributos_forms(tipo_de_item,request)

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
