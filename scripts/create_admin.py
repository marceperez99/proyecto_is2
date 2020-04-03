from django.contrib.auth.models import Permission

from roles_de_sistema.models import RolDeSistema

RolDeSistema.objects.all().delete()


rol_admin = RolDeSistema(nombre='Administrador', descripcion='Rol de Sistema de Administracion del Sistema')
rol_admin.save()
for pp in Permission.objects.filter(content_type__app_label='roles_de_sistema', codename__startswith='p'):
    rol_admin.permisos.add(pp)
rol_admin.save()