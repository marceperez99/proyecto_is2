from django.contrib.auth.models import Permission, User, Group
from django.db import models


class RolDeSistema(models.Model):
    """
    Clase un Rol de Sistema dentro del sistema. Esta clase sirve además como modelo para la creación de la Base de Datos.

    Clase Padre: models.Model

    Atributos:

        nombre: models.CharField

        descripcion: models.CharField

        permisos: models.ManyToManyField, representa la relacion de un rol con los permisos que incluye.


    """
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200)
    permisos = models.ManyToManyField(Permission)
    #creador = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ('ps_crear_rs', 'Crear nuevo Rol de Sistema'),
            ('ps_ver_rs', 'Visualizar Lista de Roles de Sistema'),
            ('ps_eliminar_rs', 'Eliminar Rol de Sistema'),
            ('ps_asignar_rs', 'Asignar Roles de Sistema '),
        ]

    def __str__(self):
        return self.nombre

    def get_permisos(self):
        """
        Metodo que retorna una lista de todos los permisos que incluye este Rol de Sistema.

        retorna: lista de Permission
        """
        return [p for p in self.permisos.all()]

    def es_utilizado(self):
        """
        Metodo que retorna True si existe algun usuario utilizando este Rol de Sistema en algun Sistema, False en caso contrario.

        returna: bool
        """
        group = Group.objects.get(name=self.nombre)
        return group.user_set.all().exists()

    def eliminar_rs(self):
        """
        Metodo que retorna True si el rol d sistema fue eliminado con exito, False en caso contrario

        :return: bool
        """
        group = Group.objects.get(name=self.nombre)
        if self.es_utilizado():
            return False
        else:
            group.delete()
            self.delete()
            return True
