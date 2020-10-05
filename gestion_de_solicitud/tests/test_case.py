from django.utils import timezone
from gestion_de_item.models import EstadoDeItem
from gestion_de_solicitud.models import EstadoSolicitud
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
    'permisos': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante', 'pa_asignar_rs',
                 'pa_cancelar_proyecto', 'pa_config_cloud', 'pa_config_sso',
                 'pa_crear_proyecto', 'pa_crear_rp', 'pa_crear_rs', 'pa_desactivar_usuario',
                 'pa_desasignar_rs', 'pa_editar_rp', 'pa_editar_rs', 'pa_eliminar_rp',
                 'pa_eliminar_rs', 'ps_ver_proyecto', 'ps_ver_rp', 'ps_ver_rs', 'ps_ver_usuarios', 'pp_f_crear_lb',
                 'pp_f_listar_lb', 'pp_f_solicitar_ruptura_de_linea_base']
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
                'Fase 1': ['pp_ver_participante', 'pp_agregar_participante', 'pp_f_crear_lb', 'pp_f_listar_lb',
                           'pp_f_solicitar_ruptura_de_linea_base'],
                'Fase 2': ['pp_ver_participante', 'pp_agregar_participante', 'pp_f_crear_lb', 'pp_f_listar_lb',
                           'pp_f_solicitar_ruptura_de_linea_base'],
                'Fase 3': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante',
                           'pp_f_crear_lb', 'pp_f_listar_lb', 'pp_f_solicitar_ruptura_de_linea_base']
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
                'prefijo': 'ti',
                'creador': 'admin',
                'fecha_de_creacion': timezone.now(),
            }
        ],
        'Fase 2': [
            {
                'nombre': 'tipoItem2',
                'descripcion': 'descripcion tipo de item 2',
                'prefijo': 'ti2',
                'creador': 'admin',
                'fecha_de_creacion': timezone.now(),
            }
        ],
        'Fase 3': [
            {
                'nombre': 'tipoItem3',
                'descripcion': 'descripcion tipo de item 3',
                'prefijo': 'ti3',
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
            'codigo': 'ti_1',
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
            'codigo': 'ti_2',
            'estado_anterior': '',
            'version': 2,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 5,
                },
                2: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 10,
                    'padres': ['ti_1']
                },
            }
        },
        {
            'tipo': 'tipoItem',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'ti_3',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item 3',
                    'descripcion': 'Descripcion',
                    'peso': 7,
                    'padres': ['ti_1']
                }
            },

        },
        {
            'tipo': 'tipoItem2',
            'estado': EstadoDeItem.APROBADO,
            'codigo': 'ti2_1',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item fase2',
                    'descripcion': 'Descripcion item ti2_1',
                    'peso': 3,
                    'antecesores': ['ti_1']
                }
            }
        },
        {
            'tipo': 'tipoItem2',
            'estado': EstadoDeItem.NO_APROBADO,
            'codigo': 'ti2_2',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 9,
                    'antecesores': ['ti_1']
                }
            }
        },
        {
            'tipo': 'tipoItem2',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'ti2_3',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item ti2_3',
                    'descripcion': 'Descripcion ti2_3',
                    'peso': 11,
                    'antecesores': ['ti_3']
                }
            },
        },
        {
            'tipo': 'tipoItem3',
            'estado': EstadoDeItem.APROBADO,
            'codigo': 'ti3_1',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item ti3_1',
                    'descripcion': 'Descripcion ti3_1',
                    'peso': 6,
                    'antecesores': ['ti2_3']
                }
            }
        },
        {
            'tipo': 'tipoItem3',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'ti3_2',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item ti3_2',
                    'descripcion': 'Descripcion ti3_2',
                    'peso': 2,
                    'antecesores': ['ti2_3']
                }
            },
        },
    ],
    'lineas_base': {
        'Fase 1': [
            {
                'nombre': 'LB_1.1',
                'estado': EstadoLineaBase.CERRADA,
                'items': ['ti_1', 'ti_2']
            },
            {
                'nombre': 'LB_1.2',
                'estado': EstadoLineaBase.CERRADA,
                'items': ['ti_3']
            }
        ],
        'Fase 2': [
            {
                'nombre': 'LB_2.1',
                'estado': EstadoLineaBase.CERRADA,
                'items': ['ti2_3']
            }
        ],
        'Fase 3': [
            {
                'nombre': 'LB_3.1',
                'estado': EstadoLineaBase.CERRADA,
                'items': ['ti3_2']
            }
        ]
    },
    'solicitudes': [
        {
            'linea_base': 'LB_1.1',
            'solicitante': 'admin',
            'descripcion': 'descripcion de la solicitud',
            'estado': EstadoSolicitud.PENDIENTE,
            'asignaciones': [
                {
                    'encargado': 'user',
                    'item': 'ti_1',
                    'cambio': 'Se necesita cambiar la descripcion'
                }
            ],
            'votos': [
                {
                    'miembro': 'admin', 'voto_a_favor': True
                },
                {
                    'miembro': 'user', 'voto_a_favor': True
                },
                {
                    'miembro': 'user2', 'voto_a_favor': True
                }
            ]
        },
        {
            'linea_base': 'LB_1.2',
            'solicitante': 'admin',
            'descripcion': 'descripcion de la solicitud',
            'estado': EstadoSolicitud.PENDIENTE,
            'asignaciones': [
                {
                    'encargado': 'user',
                    'item': 'ti_3',
                    'cambio': 'Se necesita cambiar el peso del item'
                }
            ],
            'votos': [
                {
                    'miembro': 'admin', 'voto_a_favor': True
                },
                {
                    'miembro': 'user', 'voto_a_favor': False
                }
            ]
        },
        {
            'linea_base': 'LB_2.1',
            'solicitante': 'admin',
            'descripcion': 'descripcion de la solicitud',
            'estado': EstadoSolicitud.PENDIENTE,
            'asignaciones': [
                {
                    'encargado': 'user',
                    'item': 'ti2_3',
                    'cambio': 'Se necesita cambiar el nombre'
                }
            ],
            'votos': [
                {
                    'miembro': 'admin', 'voto_a_favor': True
                }
            ]
        },
        {
            'linea_base': 'LB_3.1',
            'solicitante': 'admin',
            'descripcion': 'descripcion de la solicitud',
            'estado': EstadoSolicitud.PENDIENTE,
            'asignaciones': [
                {
                    'encargado': 'user',
                    'item': 'ti3_2',
                    'cambio': 'Se necesita cambiar la descripcion'
                }
            ],
            'votos': []
        }
    ]
}
