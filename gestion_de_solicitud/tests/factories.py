from django.contrib.auth.models import User

from gestion_de_item.models import Item
from gestion_de_solicitud.models import SolicitudDeCambio, Asignacion, Voto
from gestion_linea_base.models import LineaBase


def solicitud_de_cambio_factory(proyecto, data):
    """
    Factory que retorna objetos del tipo SolicitudDeCambio
    :param proyecto: Proyecto
    :param data: dict() de la forma:
    {
        'linea_base': 'nombre_linea_base',
        'solicitante': 'username',
        'descripcion':'descripcion de solicitud',
        'estado': 'Estado de Solicitud'
        'asignaciones':[
            {
                'encargado': 'username',
                'item': 'codigo item',
                'cambio': 'cambio necesario'
            }
        ],
        'votos': [
            {
                'miembro': 'username', 'voto_a_favor': Bool
            }
        ]
    }
    :return: SolicitudDeCambio
    """
    linea_base = LineaBase.objects.get(nombre=data['linea_base'], fase__proyecto=proyecto)
    user = User.objects.get(username=data['solicitante'])
    solicitante = proyecto.get_participante(user)
    solicitud = SolicitudDeCambio.objects.create(linea_base=linea_base, descripcion=data['descripcion'],
                                                 solicitante=solicitante, estado=data['estado'], numero_de_miembros=0)

    for asignacion in data['asignaciones']:
        asignacion_factory(solicitud, asignacion)
    if 'votos' in data.keys():
        for voto in data['votos']:
            voto_factory(solicitud, voto)
    return solicitud


def asignacion_factory(solicitud, data):
    """
    Factory que retorna objetos del tipo Asignacion
    :param solicitud: SolicitudDeCAambio
    :param data: dict() de la forma:
    {
        'encargado': 'username',
        'item': 'codigo item',
        'cambio': 'cambio necesario'
    }
    :return: Asignacion
    """
    item = Item.objects.get(codigo=data['item'])
    user = User.objects.get(username=data['encargado'])
    participante = solicitud.linea_base.fase.proyecto.get_participante(user)
    return Asignacion.objects.create(solicitud=solicitud, usuario=participante, item=item)


def voto_factory(solicitud, data):
    """
    Factory que retorna objetos del tipo Voto
    :param solicitud: SolicitudDeCambio
    :param data: dict() de la forma:
    {
        'miembro': 'username',
        'voto_a_favor': Bool
    }
    :return: Voto
    """
    user = User.objects.get(username=data['miembro'])
    participante = solicitud.linea_base.fase.proyecto.get_participante(user)
    return Voto.objects.create(solicitud=solicitud, voto_a_favor=data['voto_a_favor'], miembro=participante)
