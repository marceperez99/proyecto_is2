from datetime import datetime, timedelta

import pytz
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from gestion_de_reportes.utils import make_report
from gestion_de_solicitud.forms import GenerarReporteForm
from gestion_de_solicitud.models import SolicitudDeCambio, Voto, EstadoSolicitud
from django.shortcuts import get_object_or_404, redirect
from gestion_de_proyecto.decorators import estado_proyecto
from gestion_de_proyecto.models import Proyecto, EstadoDeProyecto
from gestion_de_solicitud.utils import aprobar_solicitud, cancelar_solicitud


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def listar_solicitudes_view(request, proyecto_id):
    """
    Vista que permite la visualizacion de las solicitudes creados dentro de un proyecto.
    La vista mostrara el nombre de la linea base afectada, la fase en donde se encuentra, y la fecha que se solicito.\n
    Argumentos:
        -request: HttpRequest.
        -proyecto_id: int, identificador unico del proyecto al que se esta accediendo.\n
    Retorna:
        -HttpResponse
    """
    solicitudes = SolicitudDeCambio.objects.filter(linea_base__fase__proyecto_id=proyecto_id).all()
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    contexto = {
        'proyecto': proyecto,
        'solicitudes_pendientes': filter(lambda x: x.estado == EstadoSolicitud.PENDIENTE, solicitudes),
        'solicitudes_aprobadas': filter(lambda x: x.estado == EstadoSolicitud.APROBADA, solicitudes),
        'solicitudes_rechazadas': filter(lambda x: x.estado == EstadoSolicitud.RECHAZADA, solicitudes),
        'breadcrumb': {
            'pagina_actual': 'Solicitudes de Cambio',
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
    Se mostrara todos los detalles de la solicitud, Descripcion, linea base afectada, en que fase se encuentra, el
    solicitante y la fecha de solicitud. Tambien se mostrara los votos a favor, en contra, como los que ya votaron y
    faltan por votar.\n
    Argumentos:
        -request: HttpRequest.
        -proyecto_id: int, identificador unico del proyecto al que se esta accediendo.
        -solicitud_id: int, identificador unico de la solicitud.\n
    Retorna:
        -HttpResponse
    """
    solicitud = get_object_or_404(SolicitudDeCambio, id=solicitud_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    participante = proyecto.get_participante(request.user)
    contexto = {
        'proyecto': proyecto,
        'solicitud': solicitud,
        'ya_voto': solicitud.ya_voto(participante),
        'mostrar_boton_votar': not solicitud.ya_voto(participante) and solicitud.estado == EstadoSolicitud.PENDIENTE,
        'breadcrumb': {
            'pagina_actual': f'Solicitud de Ruptura de {solicitud.linea_base}',
            'links': [{'nombre': proyecto.nombre, 'url': reverse('visualizar_proyecto', args=(proyecto_id,))},
                      {'nombre': 'Solicitudes de Cambio',
                       'url': reverse('solicitudes_de_cambio', args=(proyecto_id,))}]
        }
    }
    return render(request, 'gestion_de_solicitud/visualizar_solicitud.html', contexto)


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@estado_proyecto(EstadoDeProyecto.INICIADO)
def solicitud_votacion_view(request, proyecto_id, solicitud_id):
    """
    Vista que permite la votacion de una solicitud de cambio, entre los participantes del comite de cambio.
    Se verifica si el participante es miembro del comite, una ve verificado se le muestra al usuario los cambios
    propuestos en la solicitud, este tendra que dar su voto a favor o en contra, para aprobar o rechazarla respectivamete.
    Una vez hayan votados todos los del comite, se aprueba el cambio si os votos "a favor" son mayor a los votos "en contra".\n
    Argumentos:
        -request: HttpRequest
        -proyecto_id: int, identificador unico del proyecto al que se esta accediendo.
        -solicitud_id: int, identificador unico de la solicitud.
    Retorna:
        -HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    solicitud = get_object_or_404(SolicitudDeCambio, id=solicitud_id)
    participante = proyecto.get_participante(request.user)
    es_participante = proyecto.get_comite_de_cambios().es_miembro(participante)
    if not es_participante:
        return redirect('visualizar_proyecto', proyecto.id)

    if solicitud.ya_voto(participante):
        return redirect('solicitud_de_cambio', proyecto.id, solicitud.id)

    if 'voto' in request.GET.keys():
        voto = Voto(miembro=participante, solicitud_id=solicitud_id)
        if request.GET['voto'] == 'a_favor' or request.GET['voto'] == 'en_contra':
            voto.voto_a_favor = request.GET['voto'] == 'a_favor'
            voto.save()
            if solicitud.get_numero_de_votos_faltantes() == 0:
                if solicitud.get_votos_a_favor() > solicitud.get_votos_en_contra():
                    aprobar_solicitud(solicitud)
                else:
                    cancelar_solicitud(solicitud)

            return redirect('solicitudes_de_cambio', proyecto.id)

    contexto = {'proyecto': proyecto,
                'solicitud': solicitud,
                }
    return render(request, 'gestion_de_solicitud/votar_solicitud.html', contexto)


def generar_reporte(request, proyecto_id):
    if request.method == 'POST':
        form = GenerarReporteForm(request.POST)
        if form.is_valid():
            solicitudes = []
            try:
                fecha_inicial = datetime.combine(form.cleaned_data['fecha_inicial'], datetime.min.time())
                fecha_inicial = timezone.make_aware(fecha_inicial, timezone.get_default_timezone())
            except (pytz.NonExistentTimeError, pytz.AmbiguousTimeError):
                fecha_inicial = datetime.combine(form.cleaned_data['fecha_inicial'], datetime.min.time())
                fecha_inicial = fecha_inicial + timedelta(hours=1)
                fecha_inicial = timezone.make_aware(fecha_inicial, timezone.get_default_timezone())

            try:
                fecha_final = datetime.combine(form.cleaned_data['fecha_final'], datetime.min.time())
                fecha_final = timezone.make_aware(fecha_final, timezone.get_default_timezone())
            except (pytz.NonExistentTimeError, pytz.AmbiguousTimeError):
                fecha_final = datetime.combine(form.cleaned_data['fecha_final'], datetime.min.time())
                fecha_final = fecha_final + timedelta(hours=1)
                fecha_final = timezone.make_aware(fecha_final, timezone.get_default_timezone())

            solicitudesFilter = SolicitudDeCambio.objects.filter(linea_base__fase__proyecto_id=proyecto_id) \
                .filter(fecha__gte=fecha_inicial) \
                .filter(fecha__lte=fecha_final)

            if form.cleaned_data['solicitudesAprobadas']:
                solicitudes += list(solicitudesFilter.filter(estado=EstadoSolicitud.APROBADA))
            if form.cleaned_data['solicitudesPendientes']:
                solicitudes += list(solicitudesFilter.filter(estado=EstadoSolicitud.PENDIENTE))
            if form.cleaned_data['solicitudesRechazadas']:
                solicitudes += list(solicitudesFilter.filter(estado=EstadoSolicitud.RECHAZADA))

            proyecto = get_object_or_404(Proyecto, id=proyecto_id)

            return make_report('reportes/reporte_de_solicitudes.html',
                               context={'solicitudes': solicitudes, 'proyecto': proyecto,
                                        'fecha_inicial': fecha_inicial, 'fecha_final': fecha_final})
    else:
        form = GenerarReporteForm()
    contexto = {'user': request.user, 'form': form}

    return render(request, 'gestion_de_solicitud/generar_reporte.html', context=contexto)
