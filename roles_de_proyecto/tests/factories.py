from django.contrib.auth.models import Permission

from roles_de_proyecto.models import RolDeProyecto


def rol_de_proyecto_factory(data):
    """
    Factory que retorna un objeto RolDeProyecto.
    :param data: dict() de la forma {
        'nombre': 'nombre_rol',
        'descripcion': 'descripcion_rol',
        'permisos': ['pp_permiso','pp_f_permiso_1']
    }
    :return:
    """
    rol = RolDeProyecto(nombre=data['nombre'], descripcion=data['descripcion'])
    rol.save()
    for codename in data['permisos']:
        permiso = Permission.objects.get(codename=codename)
        rol.permisos.add(permiso)
    rol.save()
    return rol