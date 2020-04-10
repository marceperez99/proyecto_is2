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
from .forms import NuevoVersionItemForm, AtributoItemArchivoForm, AtributoItemCadenaForm, AtributoItemNumericoForm, \
    AtributoItemFechaForm, AtributoItemBooleanoForm


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
        'se_puede_eliminar' : item.estado == EstadoDeItem.CREADO,
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
        tipo_de_item = get_object_or_404(TipoDeItem, id=tipo_de_item_id)

        # Si es llamado con un tipo de item, permite crear un nuevo tipo de item.
        if request.method == 'POST':
            form = NuevoVersionItemForm(request.POST or None, tipo_de_item=tipo_de_item)
            atributo_forms = []
            for atributo in tipo_de_item.get_atributos():
                if type(atributo) == AtributoBinario:
                    atributo_forms.append(AtributoItemArchivoForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoCadena:
                    atributo_forms.append(AtributoItemCadenaForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoNumerico:
                    atributo_forms.append(AtributoItemNumericoForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoFecha:
                    atributo_forms.append(AtributoItemFechaForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoBooleano:
                    atributo_forms.append(AtributoItemBooleanoForm(request.POST or None, plantilla=atributo))
            if form.is_valid():
                version = form.save(commit=False)

                if item is None:
                    item = Item()
                    item.tipo_de_item = tipo_de_item
                    item.estado = EstadoDeItem.CREADO
                    item.codigo = tipo_de_item.prefijo + '_' + str(tipo_de_item.item_set.all().count() + 1)
                    item.save()

                version.version = item.version_item.all().count() + 1
                version.item = item
                version.save()
                item.version = version
                item.save()

                anterior = form.cleaned_data['relacion']
                if anterior is not None:
                    assert anterior.get_fase() == fase.fase_anterior or anterior.get_fase() == fase, "El sistema es inconsistente: El item anterior no peretence a esta fase ni a la fase anterior"

                    if anterior.get_fase() == fase.fase_anterior:
                        version.antecesores.add(anterior)
                    elif anterior.get_fase() == fase:
                        version.padres.add(anterior)

                return redirect('listar_items', proyecto_id=proyecto_id, fase_id=fase_id)
        else:
            form = NuevoVersionItemForm(request.POST or None, tipo_de_item=tipo_de_item)
            atributo_forms = []
            for atributo in tipo_de_item.get_atributos():
                if type(atributo) == AtributoBinario:
                    atributo_forms.append(AtributoItemArchivoForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoCadena:
                    atributo_forms.append(AtributoItemCadenaForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoNumerico:
                    atributo_forms.append(AtributoItemNumericoForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoFecha:
                    atributo_forms.append(AtributoItemFechaForm(request.POST or None, plantilla=atributo))
                elif type(atributo) == AtributoBooleano:
                    atributo_forms.append(AtributoItemBooleanoForm(request.POST or None, plantilla=atributo))

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
        # pasar mensaje
        if item.estado == EstadoDeItem.CREADO:
            item.estado = EstadoDeItem.ELIMINADO
            item.save()
        else:
            pass
        return redirect('listar_items', proyecto_id, fase_id)
    contexto = {'item': item.version.nombre}
    return render(request, 'gestion_de_item/eliminar_item.html', context=contexto)
