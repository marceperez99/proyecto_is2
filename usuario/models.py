from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
from roles_de_sistema.models import RolDeSistema


class Usuario(User):
    """
    Modelo proxy que extiende el modelo User de Django.

    """
    class Meta:
        proxy = True

    def asignar_rol_a_usuario(self, rs_id):
        if self.groups.all().exists():
            self.groups.all().delete()
        rs = RolDeSistema.objects.get(id=rs_id)
        print(rs.nombre)
        group = Group.objects.get(name=rs.nombre)
        self.groups.add(group)
