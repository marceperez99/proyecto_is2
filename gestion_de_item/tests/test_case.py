from django.utils import timezone
from gestion_de_item.models import EstadoDeItem
from gestion_linea_base.models import EstadoLineaBase

admin = {
    'nombre': 'Administrador', 'descripcion': 'Administrador de Sistema',
    'permisos': ['pa_asignar_rs', 'pa_cancelar_proyecto', 'pa_config_cloud', 'pa_config_sso',
                 'pa_crear_proyecto', 'pa_crear_rp', 'pa_crear_rs', 'pa_desactivar_usuario',
                 'pa_desasignar_rs', 'pa_editar_rp', 'pa_editar_rs', 'pa_eliminar_rp',
                 'pa_eliminar_rs', 'ps_ver_proyecto', 'ps_ver_rp', 'ps_ver_rs', 'ps_ver_usuarios']
}
rol_de_proyecto = {
    'nombre': 'rol',
    'descripcion': 'descripcion',
    'permisos': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
}
gerente = {'username': 'admin', 'password': 'admin', 'email': 'admin@gmail.com', 'rol_de_sistema': 'Administrador'}
user = {'username': 'user', 'password': 'admin', 'email': 'user@gmail.com', 'rol_de_sistema': 'Administrador'}
user2 = {'username': 'user2', 'password': 'admin', 'email': 'user2@gmail.com', 'rol_de_sistema': 'Administrador'}
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
                'Fase 1': ['pp_ver_participante', 'pp_agregar_participante'],
                'Fase 2': ['pp_ver_participante', 'pp_agregar_participante'],
                'Fase 3': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
            }
        },
        {
            'usuario': 'user2',
            'rol_de_proyecto': 'rol',
            'permisos': {
                'Fase 1': ['pp_ver_participante', 'pp_agregar_participante'],
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
                'prefijo': 'a',
                'creador': 'admin',
                'fecha_de_creacion': timezone.now(),
            }
        ],
        'Fase 2': [
            {
                'nombre': 'tipoItem2',
                'descripcion': 'descripcion tipo de item 2',
                'prefijo': 'b',
                'creador': 'admin',
                'fecha_de_creacion': timezone.now(),
            }
        ],
        'Fase 3': [
            {
                'nombre': 'tipoItem3',
                'descripcion': 'descripcion tipo de item 3',
                'prefijo': 'c',
                'creador': 'admin',
                'fecha_de_creacion': timezone.now(),
            }
        ]
    },
    'comite_de_cambios': ['admin', 'user', 'user2', ],
    'items': [
        {
            'tipo': 'tipoItem',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'a_1',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 5,
                }
            }
        },
        {
            'tipo': 'tipoItem',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'a_2',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 5,
                    'padres': ['a_1']
                },
            }
        },
        {
            'tipo': 'tipoItem',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'a_3',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item 3',
                    'descripcion': 'Descripcion',
                    'peso': 7,
                    'padres': ['a_1']
                }
            },

        },
        {
            'tipo': 'tipoItem2',
            'estado': EstadoDeItem.APROBADO,
            'codigo': 'b_1',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item fase2',
                    'descripcion': 'Descripcion item ti2_1',
                    'peso': 3,
                    'antecesores': ['a_2']
                }
            }
        },
        {
            'tipo': 'tipoItem2',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'b_2',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item b_2',
                    'descripcion': 'Descripcion b_2',
                    'peso': 11,
                    'antecesores': ['a_1', 'a_3']
                }
            },
        },
        {
            'tipo': 'tipoItem3',
            'estado': EstadoDeItem.APROBADO,
            'codigo': 'c_1',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item c_1',
                    'descripcion': 'Descripcion c_1',
                    'peso': 6,
                    'antecesores': ['b_2']
                }
            }
        },
    ],
    'lineas_base': {
        'Fase 1': [
            {
                'nombre': 'LB_1.1',
                'estado': EstadoLineaBase.CERRADA,
                'items': ['a_1', 'a_2', 'a_3']
            },
        ],
        'Fase 2': [
            {
                'nombre': 'LB_2.1',
                'estado': EstadoLineaBase.CERRADA,
                'items': ['b_2']
            }
        ],
    },
    'solicitudes': []
}

test_trazar_item_result = {
    'a_1': [
        {
            "fase": 'Fase 1',
            "items": [
                {
                    "codigo": 'a_1',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": ['a_2', 'a_3'],
                    "sucesores": ['b_2']
                },
                {
                    "codigo": 'a_2',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['b_1']
                },
                {
                    "codigo": 'a_3',
                    "data": {
                        "nombre": 'Nombre de item 3',
                        "tipoDeItem": 'tipoItem',
                        "peso": 7,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['b_2']
                }
            ]
        },
        {
            "fase": 'Fase 2',
            "items": [
                {
                    "codigo": 'b_1',
                    "data": {
                        "nombre": 'Nombre de item fase2',
                        "tipoDeItem": 'tipoItem2',
                        "peso": 3,
                        "estado": EstadoDeItem.APROBADO
                    },
                    "hijos": [],
                    "sucesores": []
                },
                {
                    "codigo": 'b_2',
                    "data": {
                        "nombre": 'Nombre de item b_2',
                        "tipoDeItem": 'tipoItem2',
                        "peso": 11,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['c_1']
                }
            ]
        },
        {
            "fase": 'Fase 3',
            "items": [{
                "codigo": 'c_1',
                "data": {
                    "nombre": 'Nombre de item c_1',
                    "tipoDeItem": 'tipoItem3',
                    "peso": 6,
                    "estado": EstadoDeItem.APROBADO
                },
                "hijos": [],
                "sucesores": []
            }]
        }
    ],
    'a_2': [
        {
            "fase": 'Fase 1',
            "items": [
                {
                    "codigo": 'a_1',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": ['a_2'],
                    "sucesores": []
                },
                {
                    "codigo": 'a_2',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['b_1']
                }
            ]
        },
        {
            "fase": 'Fase 2',
            "items": [{
                    "codigo": 'b_1',
                    "data": {
                        "nombre": 'Nombre de item fase2',
                        "tipoDeItem": 'tipoItem2',
                        "peso": 3,
                        "estado": EstadoDeItem.APROBADO
                    },
                    "hijos": [],
                    "sucesores": []
                }]
        },
        {
            "fase": 'Fase 3',
            "items": []
        }
    ],
    'a_3': [
        {
            "fase": 'Fase 1',
            "items": [
                {
                    "codigo": 'a_1',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": ['a_3'],
                    "sucesores": ['b_2']
                },
                {
                    "codigo": 'a_3',
                    "data": {
                        "nombre": 'Nombre de item 3',
                        "tipoDeItem": 'tipoItem',
                        "peso": 7,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['b_2']
                },
            ]
        },
        {
            "fase": 'Fase 2',
            "items": [{
                    "codigo": 'b_2',
                    "data": {
                        "nombre": 'Nombre de item b_2',
                        "tipoDeItem": 'tipoItem2',
                        "peso": 11,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['c_1']
                }]
        },
        {
            "fase": 'Fase 3',
            "items": [{
                    "codigo": 'c_1',
                    "data": {
                        "nombre": 'Nombre de item c_1',
                        "tipoDeItem": 'tipoItem3',
                        "peso": 6,
                        "estado": EstadoDeItem.APROBADO
                    },
                    "hijos": [],
                    "sucesores": []
                }]
        }
    ],
    'b_1': [
        {
            "fase": 'Fase 1',
            "items": [
                {
                    "codigo": 'a_1',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": ['a_2'],
                    "sucesores": []
                },
                {
                    "codigo": 'a_2',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['b_1']
                },

            ]
        },
        {
            "fase": 'Fase 2',
            "items": [{
                    "codigo": 'b_1',
                    "data": {
                        "nombre": 'Nombre de item fase2',
                        "tipoDeItem": 'tipoItem2',
                        "peso": 3,
                        "estado": EstadoDeItem.APROBADO
                    },
                    "hijos": [],
                    "sucesores": []
                }]
        },
        {
            "fase": 'Fase 3',
            "items": []
        }
    ],
    'b_2': [
        {
            "fase": 'Fase 1',
            "items": [
                {
                    "codigo": 'a_1',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": ['a_3'],
                    "sucesores": ['b_2']
                },
                {
                    "codigo": 'a_3',
                    "data": {
                        "nombre": 'Nombre de item 3',
                        "tipoDeItem": 'tipoItem',
                        "peso": 7,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['b_2']
                }
            ]
        },
        {
            "fase": 'Fase 2',
            "items": [{
                    "codigo": 'b_2',
                    "data": {
                        "nombre": 'Nombre de item b_2',
                        "tipoDeItem": 'tipoItem2',
                        "peso": 11,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['c_1']
                }]
        },
        {
            "fase": 'Fase 3',
            "items": [{
                    "codigo": 'c_1',
                    "data": {
                        "nombre": 'Nombre de item c_1',
                        "tipoDeItem": 'tipoItem3',
                        "peso": 6,
                        "estado": EstadoDeItem.APROBADO
                    },
                    "hijos": [],
                    "sucesores": []
                }]
        }
    ],
    'c_1': [
        {
            "fase": 'Fase 1',
            "items": [
                {
                    "codigo": 'a_1',
                    "data": {
                        "nombre": 'Nombre de item',
                        "tipoDeItem": 'tipoItem',
                        "peso": 5,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": ['a_3'],
                    "sucesores": ['b_2']
                },
                {
                    "codigo": 'a_3',
                    "data": {
                        "nombre": 'Nombre de item 3',
                        "tipoDeItem": 'tipoItem',
                        "peso": 7,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['b_2']
                }
            ]
        },
        {
            "fase": 'Fase 2',
            "items": [{
                    "codigo": 'b_2',
                    "data": {
                        "nombre": 'Nombre de item b_2',
                        "tipoDeItem": 'tipoItem2',
                        "peso": 11,
                        "estado": EstadoDeItem.EN_LINEA_BASE
                    },
                    "hijos": [],
                    "sucesores": ['c_1']
                }]
        },
        {
            "fase": 'Fase 3',
            "items": [{
                    "codigo": 'c_1',
                    "data": {
                        "nombre": 'Nombre de item c_1',
                        "tipoDeItem": 'tipoItem3',
                        "peso": 6,
                        "estado": EstadoDeItem.APROBADO
                    },
                    "hijos": [],
                    "sucesores": []
                }]
        }
    ]
}
