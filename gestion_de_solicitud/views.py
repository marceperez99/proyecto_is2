from django.contrib.auth.decorators import permission_required, login_required
from django.forms import inlineformset_factory
from django.shortcuts import render
from django.urls import reverse
from gestion_de_solicitud.models import SolicitudDeCambio, Voto
from django.shortcuts import get_object_or_404, redirect
from gestion_de_proyecto.decorators import estado_proyecto
from gestion_de_proyecto.models import Proyecto, EstadoDeProyecto


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def listar_solicitudes_view(request, proyecto_id):
    """
        Vista que permite la visualizacion de las solicitudes creados dentro de un proyecto.
    """
    solicitudes = SolicitudDeCambio.objects.filter(linea_base__fase__proyecto_id=proyecto_id).all()
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    contexto = {
        'proyecto': proyecto,
        'solicitudes': solicitudes,
        'breadcrumb': {
            'pagina_actual': 'Fases',
            'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))}]
        }
    }
    return render(request, 'gestion_de_solicitud/listar_solicitudes.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def solicitud_view(request, proyecto_id, solicitud_id):
    """
        Vista que permite la visualizacion de una solicitud en particular.
    """
    solicitud = get_object_or_404(SolicitudDeCambio, id=solicitud_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    participante = proyecto.get_participante(request.user)
    contexto = {
        'proyecto': proyecto,
        'solicitud': solicitud,
        'usuario_ha_votado': solicitud.ya_voto(participante),
        'breadcrumb': {
            'pagina_actual': 'Fases',
            'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))}]
        }
    }
    return render(request, 'gestion_de_solicitud/visualizar_solicitud.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def solicitud_votacion_view(request, proyecto_id, solicitud_id):
    """
    :param request:
    :param proyecto_id:
    :param solicitud_id:
    :return:
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    solicitud = get_object_or_404(SolicitudDeCambio, id=solicitud_id)
    participante = proyecto.get_participante(request.user)
    es_participante = proyecto.get_comite_de_cambios().es_miembro(participante)
    if not es_participante:
        return redirect('visualizar_proyecto', proyecto.id)

    if solicitud.ya_voto(participante):
        return redirect('solicitud_de_cambio', proyecto.id)

    if 'voto' in request.GET.keys():
        voto = Voto(miembro=participante, solicitud_id=solicitud_id)
        if request.GET['voto'] == 'a_favor' or request.GET['voto'] == 'en_contra':
            voto.voto_a_favor = request.GET['voto'] == 'a_favor'
            voto.save()
            return redirect('solicitudes_de_cambio', proyecto.id)

    contexto = {'proyecto': proyecto,
                'solicitud': solicitud,
                }
    return render(request, 'gestion_de_solicitud/votar_solicitud.html', contexto)
