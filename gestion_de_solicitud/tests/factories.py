from gestion_de_solicitud.models import SolicitudDeCambio


def solicitud_de_cambio_factory(linea_base,solicitante, data):
    solicitud = SolicitudDeCambio.objects.create(linea_base=linea_base,descripcion=data['descripcion'],
                                                 solicitante=solicitante, estado=data['estado'],numero_de_miembros=0)

    return solicitud
    pass