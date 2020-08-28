from django.contrib.auth.models import User
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_fase.factories import fase_factory
from gestion_de_item.factories import item_factory
from gestion_de_proyecto.models import Participante, Proyecto
from gestion_de_tipo_de_item.factories import tipo_de_item_factory
from gestion_de_tipo_de_item.models import TipoDeItem
from roles_de_proyecto.models import RolDeProyecto


def proyecto_factory(data, fecha_de_creacion=timezone.now()):
    """
    Factory que retorna un objeto Proyecto
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
            'tipos_de_item': {
                'fase1': [
                    {}
                ],
                ...
            },
            items: {
                'fase1': [
                    {
                    }
                ]
            }

    }
    :return:
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

    for fase, tipos in data['tipos_de_item'].items():
        fase = Fase.objects.get(nombre=fase)
        for tipo in tipos:
            tipo_de_item_factory(fase, tipo)

    for item in data['items']:
        tipo = TipoDeItem.objects.get(nombre=item['tipo'])
        item_factory(tipo, item)


def participante_factory(proyecto, data):
    if isinstance(data, Participante): return data
    usuario = User.objects.get(username=data['usuario'])
    rol = RolDeProyecto.objects.get(nombre=data['rol_de_proyecto'])
    participante = Participante.objects.create(usuario=usuario, rol=rol, proyecto=proyecto)
    permisos = {Fase.objects.get(nombre=fase): permisos for fase, permisos in data['permisos']}
    participante.asignar_rol_de_proyecto(rol, permisos)
    return participante
