from django.contrib.auth.models import Permission
from django.db import models

# Create your models here.


class RolDeProyecto(models.Model):
    """
    Clase un Rol de Proyecto dentro del sistema. Esta clase sirve además como modelo para la creación de la Base de Datos.

    Clase Padre: models.Model

    Atributos:

        nombre: models.CharField

        descripcion: models.CharField

        permisos: models.ManyToManyField, representa la relacion de un rol con los permisos que incluye.


    """
    nombre = models.CharField(max_length = 50, unique=True)
    descripcion = models.CharField(max_length = 200)
    permisos = models.ManyToManyField(Permission)

    def __str__(self):
        return self.nombre

    def get_permisos(self):
        """
        Metodo que retorna una lista de todos los permisos que incluye este Rol de Proyecto.

        retorna: lista de Permission
        """
        return [p for p in self.permisos.all()]