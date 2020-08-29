from django.contrib.auth.models import User
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_fase.tests.factories import fase_factory
from gestion_de_item.tests.factories import item_factory
from gestion_de_proyecto.models import Participante, Proyecto, Comite
from gestion_de_solicitud.tests.factories import solicitud_de_cambio_factory
from gestion_de_tipo_de_item.tests.factories import tipo_de_item_factory
from gestion_de_tipo_de_item.models import TipoDeItem
from gestion_linea_base.tests.factories import linea_base_factory
from roles_de_proyecto.models import RolDeProyecto


def proyecto_factory(data, fecha_de_creacion=timezone.now()):
    """
    Factory que retorna un objeto Proyecto
    :param fecha_de_creacion: Fecha de creacion del Proyecto
    :param data: dict() de la forma
    {
        'nombre':'nombre_proyecto',
        'descripcion':'descripcion_proyecto',
        'gerente': 'username',
        'estado': 'Estado_Proyecto',
        'fases':[
            {
            'nombre':'nombre_fase',
            'descripcion': 'descripcion_fase',
            'puede_cerrarse': True,
            'fase_cerrada': True,
            },{...},...],
            'participantes': [
                {
                    'usuario':'username',
                    'rol_de_proyecto':'nombre de rol'
                    'permisos': {
                        'nombre_fase':['pp_fase','permiso'],
                        'nombre_fase2':['pp_fase','permiso'],
                    }
                }
            ],
            'comite_de_cambios':['user1','user2'],
            'tipos_de_item': {
                'fase1': [
                    {
                        Tipo de Item, ver gestion_de_tipo_de_item/factories.py
                    }
                ],
                ...
            },
            items: {
                'fase1': [
                    {Item, ver item_factory}
                ]
            },
            'lineas_base':{
                'fase1': [
                    {LineaBase, ver linea_base_factory()}
                ]
            },
            'solicitudes':[
                {SolicitudDeCambio, ver solicitud_de_cambio_factory},...
            ]
    }
    :return: Proyecto
    """
    gerente = User.objects.get(username=data['gerente'])
    creador = User.objects.get(username=data['creador'])
    proyecto = Proyecto.objects.create(nombre=data['nombre'], descripcion=data['descripcion'],
                                       fecha_de_creacion=fecha_de_creacion,
                                       gerente=gerente, creador=creador, estado=data['estado'])

    fase_anterior = None
    for fase in data['fases']:
        fase_anterior = fase_factory(proyecto, fase_anterior, fase)
    gerente = Participante.objects.create(usuario=gerente, proyecto=proyecto)

    comite_factory(proyecto, data['comite_de_cambios'])

    for participante in data['participantes']:
        participante_factory(proyecto, participante)

    for fase, tipos in data['tipos_de_item'].items():
        fase = Fase.objects.get(nombre=fase)
        for tipo in tipos:
            tipo_de_item_factory(fase, tipo)

    for item in data['items']:
        item_factory(item)

    for fase, lineas_base in data['lineas_base'].items():
        fase = Fase.objects.get(nombre=fase)
        for linea_base in lineas_base:
            linea_base_factory(fase, linea_base)

    if 'solicitudes' in data.keys():
        for solicitud in data['solicitudes']:
            solicitud_de_cambio_factory(proyecto, solicitud)

    return proyecto

def participante_factory(proyecto, data):
    """
    Factory que retorna objetos del tipo Participante
    :param proyecto: Proyecto
    :param data: dict() de la forma:
        {
            'usuario':'username',
            'rol_de_proyecto':'nombre de rol'
            'permisos': {
                'nombre_fase':['pp_fase','permiso'],
                'nombre_fase2':['pp_fase','permiso'],
            }
        }
    :return: Participante
    """
    if isinstance(data, Participante): return data
    usuario = User.objects.get(username=data['usuario'])
    rol = RolDeProyecto.objects.get(nombre=data['rol_de_proyecto'])
    participante = Participante.objects.create(usuario=usuario, rol=rol, proyecto=proyecto)
    permisos = {Fase.objects.get(nombre=fase): permisos for fase, permisos in data['permisos'].items()}
    participante.asignar_rol_de_proyecto(rol, permisos)
    return participante


def comite_factory(proyecto, data):
    """
    Factory que retorna objetos del tipo Comite
    :param proyecto: Proyecto
    :param data: list() de la forma: ['username','username1']
    :return:
    """
    comite = Comite.objects.create(proyecto=proyecto)
    comite.save()
    for miembro in data:
        user = User.objects.get(username=miembro)
        participante = proyecto.get_participante(user)
        comite.miembros.add(participante)

    return comite
