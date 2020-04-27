from django.contrib.auth.models import Permission, Group
from roles_de_sistema.models import RolDeSistema
ADMIN_ROLE_NAME = 'Administrador'
admins = []
if Group.objects.filter(name=ADMIN_ROLE_NAME).exists():

    grupo = Group.objects.get(name=ADMIN_ROLE_NAME)
    admins = list(grupo.user_set.all())
    grupo.delete()

if RolDeSistema.objects.filter(nombre=ADMIN_ROLE_NAME).exists():
    RolDeSistema.objects.get(nombre=ADMIN_ROLE_NAME).delete()

rol_admin = RolDeSistema(nombre=ADMIN_ROLE_NAME, descripcion='Rol de Sistema de Administracion del Sistema')
rol_admin.save()
ps_lista = Permission.objects.filter(content_type__app_label='roles_de_sistema', codename__startswith='p')

rol_admin.permisos.add(*ps_lista)
rol_admin.save()

grupo = Group.objects.get(name=ADMIN_ROLE_NAME)
if admins:
    print("Asignando de vuelta Rol de Administrador a:")
    for user in admins:
        print(user.get_full_name())
        user.groups.add(grupo)
