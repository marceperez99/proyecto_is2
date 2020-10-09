from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.forms import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from gestion_de_fase.decorators import fase_abierta
from gestion_de_proyecto.decorators import estado_proyecto
from gestion_de_proyecto.models import Comite, Proyecto, EstadoDeProyecto
from gestion_de_solicitud.models import SolicitudDeCambio, EstadoSolicitud, Asignacion
from gestion_linea_base.forms import AsignacionForm, SolicitudForm, LineaBaseForm
from gestion_linea_base.models import LineaBase, EstadoLineaBase
from roles_de_proyecto.decorators import pp_requerido_en_fase
from gestion_de_fase.models import Fase
from django.urls import reverse
from gestion_de_item.models import EstadoDeItem
from gestion_linea_base.utils import *


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase("pp_f_solicitar_ruptura_de_linea_base")
@estado_proyecto(EstadoDeProyecto.INICIADO)
@fase_abierta()
def solicitar_rompimiento_view(request, proyecto_id, fase_id, linea_base_id):
    """
    Vista que permite la creación de nuevas solicitudes de rompimiento de lineas bases cerradas.

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, id del proyecto
        - fase_id: int, id de la fase
        - linea_base_id: int, id de la linea base
    Retorna:
        - HttpResponse
    """
    # TODO: Verificar que la linea base no este Rota

    linea_base = LineaBase.objects.get(id=linea_base_id)

    if linea_base.estado != EstadoLineaBase.CERRADA:
        return redirect('visualizar_linea_base', proyecto_id, fase_id, linea_base_id)

    fase = Fase.objects.get(id=fase_id)
    items = linea_base.items.all()
    asignacion_formset = formset_factory(AsignacionForm, extra=items.count(), can_delete=False)

    proyecto = Proyecto.objects.get(id=proyecto_id)

    if request.method == 'POST':
        solicitud_form = SolicitudForm(request.POST)
        formset = asignacion_formset(request.POST, form_kwargs={'proyecto_id': proyecto_id, 'fase_id': fase_id})
        print(request.POST)
        if solicitud_form.is_valid() and all(form.is_valid() for form in formset):

            solicitud = SolicitudDeCambio()
            solicitud.descripcion = solicitud_form.cleaned_data['razon_rompimiento']
            solicitud.solicitante = proyecto.get_participante(request.user)
            solicitud.estado = EstadoSolicitud.PENDIENTE
            solicitud.fecha = timezone.now()

            # Get a Linea Base
            solicitud.linea_base = linea_base
            # Consigue el numero de miembros
            comite = Comite.objects.get(proyecto=proyecto)
            solicitud.numero_de_miembros = comite.miembros.count()

            solicitud.save()
            count = 0
            for form in formset:
                if form.cleaned_data and form.cleaned_data['modificar']:
                    asignacion = Asignacion()
                    asignacion.usuario = form.cleaned_data['usuario']
                    asignacion.solicitud = solicitud
                    asignacion.item = items[count]
                    asignacion.motivo = form.cleaned_data['motivo']
                    asignacion.save()
                count = count + 1

            return redirect('visualizar_linea_base', proyecto_id, fase_id, linea_base_id)
    else:
        solicitud_form = SolicitudForm()

        formset = asignacion_formset(form_kwargs={'proyecto_id': proyecto_id, 'fase_id': fase_id})
        for form, item in zip(formset, items):
            form.item = item

    contexto = {'formset': formset,
                'solicitud_form': solicitud_form,
                'linea_base': linea_base,
                'len': len(formset),
                'breadcrumb': {'pagina_actual': 'Solicitar Rompimiento',
                               'links': [
                                   {'nombre': proyecto.nombre,
                                    'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                   {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                   {'nombre': fase.nombre,
                                    'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                   {'nombre': 'Lineas Base',
                                    'url': reverse('listar_linea_base', args=(proyecto.id, fase.id))},
                                   {'nombre': linea_base.nombre,
                                    'url': reverse('visualizar_linea_base',
                                                   args=(proyecto.id, fase.id, linea_base.id))},
                               ]}
                }
    return render(request, 'gestion_linea_base/solicitar_rompimiento.html', context=contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_crear_lb')
@fase_abierta()
def nueva_linea_base_view(request, proyecto_id, fase_id):
    """
    Vista que permite la creación de nuevas Lineas de Base.

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, id del proyecto
        - fase_id: int, id de la fase
    Retorna:
        - HttpResponse
    """
    # TODO: Marcos incluir en la planilla
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    if request.method == 'POST':
        form = LineaBaseForm(request.POST, proyecto=proyecto, fase=fase)
        if form.is_valid():
            lineabase = form.save()
            lineabase.fase = get_object_or_404(Fase, id=fase_id)
            lineabase.estado = EstadoLineaBase.CERRADA
            lineabase.nombre = create_nombre_LB(proyecto=proyecto, fase=fase)
            for l in lineabase.items.all():
                l.estado = EstadoDeItem.EN_LINEA_BASE
                l.save()
                print(str(l) + " - " + l.estado)
            lineabase.save()

            return redirect("visualizar_fase", proyecto_id=proyecto_id, fase_id=fase_id)
    else:
        form = LineaBaseForm(proyecto=proyecto, fase=fase)
    contexto = {'formulario': form,
                'breadcrumb': {'pagina_actual': 'Nueva Linea Base',
                               'links': [
                                   {'nombre': proyecto.nombre,
                                    'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                   {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                   {'nombre': fase.nombre,
                                    'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                   {'nombre': 'Lineas Base',
                                    'url': reverse('listar_linea_base', args=(proyecto.id, fase.id))},
                               ]}
                }

    return render(request, 'gestion_linea_base/nuevo_linea_base.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_listar_lb')
@estado_proyecto(EstadoDeProyecto.INICIADO, EstadoDeProyecto.CANCELADO, EstadoDeProyecto.FINALIZADO)
def listar_linea_base_view(request, proyecto_id, fase_id):
    """
    Vista que permite la visualizacion de los items creados dentro de la fase.
    Si el usuario cuenta con el permiso de proyecto

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, id del proyecto
        - fase_id: int, id de la fase
    Retorna:
        - HttpResponse
    """
    # TODO: Marcos incluir en la planilla
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    lis_lb = LineaBase.objects.filter(fase=fase)
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'list_lb': lis_lb,
        # 'permisos': participante.get_permisos_por_fase_list(fase) + participante.get_permisos_de_proyecto_list(),
        'breadcrumb': {'pagina_actual': 'Lineas Base',
                       # 'permisos': participante.get_permisos_por_fase_list(fase),
                       'links': [
                           {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                           {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                           {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))}
                       ]
                       }
    }
    return render(request, 'gestion_linea_base/listar_linea_base.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase('pp_f_listar_lb')
@estado_proyecto(EstadoDeProyecto.INICIADO, EstadoDeProyecto.CANCELADO, EstadoDeProyecto.FINALIZADO)
def visualizar_linea_base_view(request, proyecto_id, fase_id, linea_base_id):
    """
    Vista que permite la visualizacion de la Linea de Base y los items que la componen.
    Si el usuario cuenta con el permiso de proyecto

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, id del proyecto
        - fase_id: int, id de la fase
        - linea_base_id: int, id de la linea base
    Retorna:
        - HttpResponse
    """
    # TODO: Marcos registrar en planilla
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(proyecto.fase_set, id=fase_id)
    lineabase = get_object_or_404(LineaBase, id=linea_base_id)
    print("cantidad de items")
    print(lineabase.items.all().__len__())
    contexto = {
        'user': request.user,
        'proyecto': proyecto,
        'fase': fase,
        'lineabase': lineabase,
        'linea_base_cerrada': lineabase.estado == EstadoLineaBase.CERRADA,
        # 'permisos': participante.get_permisos_por_fase_list(fase) + participante.get_permisos_de_proyecto_list(),
        'breadcrumb': {'pagina_actual': lineabase.nombre,
                       # 'permisos': participante.get_permisos_por_fase_list(fase),
                       'links': [
                           {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                           {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                           {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                           {'nombre': 'Lineas Base',
                            'url': reverse('listar_linea_base', args=(proyecto.id, fase.id))},
                       ]
                       }
    }
    return render(request, 'gestion_linea_base/ver_linea_base.html', contexto)
