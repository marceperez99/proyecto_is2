from django.contrib.auth.models import Permission, User
from django.db import models

from gestion_de_fase.models import Fase


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
    #creador = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [('ps_crear_rp', 'Crear Rol de Proyecto'),
                       ('ps_editar_rp', 'Editar Rol de Proyecto'),
                       ('ps_eliminar_rp', 'Eliminar Rol de Proyecto'),
                       ('ps_ver_rp', 'Visualizar Rol de Proyecto')]

    def __str__(self):
        return f'{self.nombre}: {self.permisos}'

    def asignar_permisos(self, permisos):
        """
        TODO falta hacer
        :param permisos:
        :return:
        """
        for permiso in permisos:
            self.permisos.add(permiso)

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
        return False

    def tiene_pp(self, permiso):
        """TODO"""
        return self.permisos.filter(codename=permiso).exists()

    def get_pp_por_proyecto(self):
        """
        Metodo que retorna todos los permisos de proyecto que son aplicables al proyecto en general
        asignados a un Rol de Proyecto.
        TODO
        :return:
        """
        return self.permisos.filter(codename__startswith='pp_').filter(codename__regex=r'pp_[^f_]')

    def get_pp_por_fase(self):
        """
        Metodo que retorna todos los permisos de proyecto que son aplicables solo dentro de una fase de un proyecto.
        TODO
        :return:
        """
        return self.permisos.filter(codename__startswith='pp_f_')


class PermisosPorFase(models.Model):
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    permisos = models.ManyToManyField(Permission)

    def __str__(self):
        return f'{self.fase}: {self.permisos}'

    def asignar_permisos_de_proyecto(self, permisos):
        """
        Metodo que recibe como parametro una lista de permisos a asignar a un usuario en una fase
        :param permisos:
        :return:
        """
        if isinstance(permisos, list):
            for permiso in permisos:
                if isinstance(permiso, str):
                    permiso = Permission.objects.get(codename=permiso)
                self.permisos.add(permiso)
        elif isinstance(permisos, str):
            permiso = Permission.objects.get(codename=permisos)
            self.permisos.add(permiso)
        else:
            raise Exception('Tipo de dato inesperado')

    def tiene_pp(self, permiso):
        """TODO"""
        return self.permisos.filter(codename=permiso).exists()