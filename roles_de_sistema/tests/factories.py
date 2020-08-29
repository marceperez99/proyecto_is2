from django.contrib.auth.models import Permission

from roles_de_sistema.models import RolDeSistema


def rol_de_sistema_factory(nombre, descripcion, permisos):
    """
    Factory que retorna objetos del tipo RolDeSistema.
    :param nombre:
    :param descripcion:
    :param permisos:
    :return:
    """
    rol = RolDeSistema(nombre=nombre, descripcion=descripcion)
    rol.save()
    for pp in Permission.objects.filter(codename__in=permisos):
        rol.permisos.add(pp)
    rol.save()
    return rol