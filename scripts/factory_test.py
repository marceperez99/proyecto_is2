from django.utils import timezone

from gestion_de_proyecto.tests.factories import proyecto_factory
from roles_de_proyecto.tests.factories import rol_de_proyecto_factory
from usuario.tests.factories import user_factory

admin = rol_de_proyecto_factory({
    'nombre': 'Administrador',
    'descripcion': 'Administrador de Sistema',
    'permisos': ['pa_asignar_rs', 'pa_cancelar_proyecto', 'pa_config_cloud', 'pa_config_sso',
                 'pa_crear_proyecto', 'pa_crear_rp', 'pa_crear_rs', 'pa_desactivar_usuario',
                 'pa_desasignar_rs', 'pa_editar_rp', 'pa_editar_rs', 'pa_eliminar_rp',
                 'pa_eliminar_rs', 'ps_ver_proyecto', 'ps_ver_rp', 'ps_ver_rs', 'ps_ver_usuarios']
})
rol_de_proyecto = rol_de_proyecto_factory({
    'nombre': 'rol',
    'descripcion': 'descripcion',
    'permisos': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
})
gerente = user_factory('admin', 'admin', 'marc@gmail.com', admin)
usuario = user_factory('user', 'admin', 'user@gmail.com', rol_de_proyecto)
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
            }
        ]
    },
    'items': []
}
proyecto_factory(proyecto)
