from gestion_de_item.models import EstadoDeItem
from gestion_de_solicitud.models import EstadoSolicitud, SolicitudDeCambio
from gestion_linea_base.models import EstadoLineaBase


def cancelar_solicitud(solicitud):
    """
    # TODO: Cargar en la planilla
    Funcion utilitaria que implementa la cancelacion de una solicitud de Ruptura de Linea Base
    Argumentos:
     - solicitud: SolicitudDeCambio
    """
    assert solicitud.estado == EstadoSolicitud.PENDIENTE
    solicitud.estado = EstadoSolicitud.RECHAZADA
    solicitud.save()
    # TODO: notificar a solicitante que la solicitud fue cancelada


def aprobar_solicitud(solicitud: SolicitudDeCambio):
    """
    Funcion utilitaria que aprueba la solicitud de ruptura de linea base
    Argumentos:
     - solicitud: Solicitud

    """
    assert solicitud.estado == EstadoSolicitud.PENDIENTE

    linea_base = solicitud.linea_base

    # se solicita la modificacion de los items especificados
    for asignacion in solicitud.get_items_a_modificar():
        asignacion.item.solicitar_modificacion(asignacion.usuario)

        for hijo in asignacion.item.get_hijos():
            if hijo.estado in [EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE]:
                hijo.solicitar_revision()

        for sucesor in asignacion.item.get_sucesores():
            if sucesor.estado in [EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE]:
                # TODO: se necesita poner en estado Comprometida a la LB
                sucesor.solicitar_revision()

    # Se ponen los demas items en la linea base en revision
    for item in linea_base.items.all():
        if item.estado == EstadoDeItem.EN_LINEA_BASE:
            item.solicitar_revision()

    solicitud.estado = EstadoSolicitud.APROBADA
    solicitud.save()
    for s in SolicitudDeCambio.objects.filter(linea_base=solicitud.linea_base, estado=EstadoSolicitud.PENDIENTE):
        s.estado = EstadoSolicitud.RECHAZADA
        s.save()

    linea_base.estado = EstadoLineaBase.ROTA
    linea_base.save()
    # TODO notificar a usuarios de cambios
