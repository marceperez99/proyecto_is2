from gestion_de_item.models import EstadoDeItem
from gestion_de_solicitud.models import EstadoSolicitud, SolicitudDeCambio
from gestion_linea_base.models import EstadoLineaBase

# TODO: Cargar en la planilla
def cancelar_solicitud(solicitud):
    """
    Funcion utilitaria que implementa la cancelacion de una solicitud de Ruptura de Linea Base
    :param solicitud: SolicitudDeCambio
    :return:
    """
    assert solicitud.estado == EstadoSolicitud.PENDIENTE
    solicitud.estado = EstadoSolicitud.RECHAZADA
    # TODO: notificar a solicitante que la solicitud fue cancelada


def aprobar_solicitud(solicitud: SolicitudDeCambio):
    """
    Funcion utilitaria que aprueba la solicitud de ruptura de linea base
    :param solicitud:
    :return:
    """
    assert solicitud.estado == EstadoSolicitud.PENDIENTE

    linea_base = solicitud.linea_base
    linea_base.estado = EstadoLineaBase.ROTA

    for asignacion in solicitud.get_items_a_modificar():
        asignacion.item.solicitar_modificacion(asignacion.usuario)

        for hijo in asignacion.item.get_hijos():
            if hijo.estado in [EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE]:
                hijo.solicitar_revision()

        for sucesor in asignacion.item.get_sucesores():
            if sucesor.estado in [EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE]:
                sucesor.solicitar_revision()

    solicitud.estado = EstadoSolicitud.APROBADA
    # TODO notificar a usuarios de cambios


