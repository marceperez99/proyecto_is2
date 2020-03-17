from django.contrib.auth.models import Permission
from django.db import models


class RolDeProyecto(models.Model):
    """
    Clase un Rol de Proyecto dentro del sistema. Esta clase sirve además como modelo para la creación de la Base de Datos.

    Clase Padre: models.Model

    Atributos:

        nombre: models.CharField

        descripcion: models.CharField

        permisos: models.ManyToManyField, representa la relacion de un rol con los permisos que incluye.


    """
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200)
    permisos = models.ManyToManyField(Permission)

    class Meta:
        permissions = [('ps_crear_rp', 'Crear Rol de Proyecto'),
                       ('ps_editar_rp', 'Editar Rol de Proyecto'),
                       ('ps_eliminar_rp', 'Eliminar Rol de Proyecto'),
                       ('ps_ver_rp', 'Visualizar Rol de Proyecto')]

    def __str__(self):
        return self.nombre

    def get_permisos(self):
        """
        Metodo que retorna una lista de todos los permisos que incluye este Rol de Proyecto.

        retorna: lista de Permission
        """
        return [p for p in self.permisos.all()]

    def es_utilizado(self):
        """
        Metodo que retorna True si existe algun usuario utilizando este Rol de Proyecto en algun Proyecto, False en caso contrario.

        returna: bool
        """
        #TODO: Falta agregar la logica de esta seccion
        return True
