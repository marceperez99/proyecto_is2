from django.contrib.auth.decorators import login_required, permission_required
from .forms import LineaBaseForm
from django.shortcuts import render, get_object_or_404, redirect
from gestion_de_fase.models import Fase
from .models import LineaBase, EstadoLineaBase
from gestion_de_proyecto.models import Proyecto
from django.urls import reverse
from gestion_de_item.models import Item, EstadoDeItem


@login_required
#@permission_required('roles_de_sistema.pa_crear_proyecto', login_url='sin_permiso')
def nueva_linea_base_view(request, proyecto_id, fase_id):

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    if request.method == 'POST':
        form = LineaBaseForm(request.POST, proyecto=proyecto, fase=fase)
        if form.is_valid():
            lineabase = form.save()
            lineabase.fase = get_object_or_404(Fase, id=fase_id)
            lineabase.estado = EstadoLineaBase.CERRADO
            lineabase.nombre = LineaBase.create_nombre(self=None, proyecto=proyecto, fase=fase)
            for l in lineabase.items.all():
                l.estado = EstadoDeItem.EN_LINEA_BASE
                l.save()
                print(str(l)+" - "+l.estado)
            lineabase.save()

            return redirect("visualizar_fase", proyecto_id=proyecto_id, fase_id=fase_id)
    else:
        form = LineaBaseForm(proyecto=proyecto, fase=fase)
    contexto = {'formulario': form,
                'breadcrumb': {'pagina_actual': 'Nueva Linea Base',
                               'links': [
                                {'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto.id,))},
                                {'nombre': 'Fases', 'url': reverse('listar_fases', args=(proyecto.id,))},
                                {'nombre': fase.nombre, 'url': reverse('visualizar_fase', args=(proyecto.id, fase.id))},
                                {'nombre': 'Lineas Base', 'url': reverse('listar_linea_base', args=(proyecto.id, fase.id))},
                               ]}
                }

    return render(request, 'gestion_linea_base/nuevo_linea_base.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
# @pp_requerido_en_fase('pu_f_ver_fase')
# @estado_proyecto(EstadoDeProyecto.INICIADO)
def listar_linea_base_view(request, proyecto_id, fase_id):
    """
    Vista que permite la visualizacion de los items creados dentro de la fase.
    Si el usuario cuenta con el permiso de proyecto

    """
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

