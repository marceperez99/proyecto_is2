from django.utils import timezone

from gestion_de_proyecto.factories import proyecto_factory
from roles_de_proyecto.tests import rol_de_proyecto_factory
from usuario.tests import user_factory

gerente = user_factory('admin', 'admin', 'marc@gmail.com')
usuario = user_factory('user', 'admin', 'user@gmail.com')
rol_de_proyecto = rol_de_proyecto_factory({
    'nombre': 'rol',
    'descripcion': 'descripcion',
    'permisos': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
})
proyecto = {
    'gerente': 'admin',
    'nombre': 'Proyecto',
    'estado': 'Iniciado',
    'descripcion': 'Proyecto de prueba',
    'creador': 'admin',
    'fases': [
        {
            'nombre': 'Fase 1',
            'descripcion': 'Descripcion fase 1',
            'puede_cerrarse': False,
            'fase_cerrada': False,
        }, {
            'nombre': 'Fase 2',
            'descripcion': 'Descripcion fase 2',
            'puede_cerrarse': False,
            'fase_cerrada': False,
        }, {
            'nombre': 'Fase 3',
            'descripcion': 'Descripcion fase 3',
            'puede_cerrarse': False,
            'fase_cerrada': False,
        }
    ],
    'participantes': [
        {
            'usuario': 'user',
            'rol_de_proyecto': 'rol',
            'permisos': {
                'Fase 2': ['pp_ver_participante', 'pp_agregar_participante'],
                'Fase 3': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
            }
        }
    ],
    'tipos_de_item': {
        'Fase 1': [
                    {
                        'nombre': 'tipoItem',
                        'descripcion': 'descripcion',
                        'prefijo': 'ti',
                        'creador': 'admin',
                        'fecha_de_creacion': timezone.now(),
                        'atributos_dinamicos': [
                            {
                                'tipo': 'archivo',
                                'nombre': 'archivito',
                                'requerido': True,
                                'max_tamaño': 5,
                            }, {
                                'tipo': 'cadena',
                                'nombre': 'texto',
                                'requerido': True,
                                'max_longitud': 10,
                            }, {
                                'tipo': 'booleano',
                                'nombre': 'check',
                            }, {
                                'tipo': 'archivo',
                                'nombre': 'nombre del campo',
                                'requerido': False,
                                'max_digitos': 3,
                                'max_decimales': 3,
                            }, {
                                'tipo': 'fecha',
                                'nombre': 'fecha',
                                'requerido': True
                            }
                        ]
                    }
                ]
    },
    'items': []
}
proyecto_factory(proyecto)
