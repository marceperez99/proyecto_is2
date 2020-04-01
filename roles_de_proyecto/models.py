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
    #creador = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    def asignar_permisos(self, permisos):
        """
        Metodo que asigna un conjunto de permisos de proyecto al rol.

        Args:
            permisos: lista de objetos del tipo Permission.
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
        Metodo que verifica si el Rol de Proyecto esta siendo utilizado en algun Proyecto.

        Retorna:
            True si el rol esta asignado a un participante de un proyecto.\n
            False en caso contrario.
        """
        return self.participante_set.all().exists()

    def tiene_pp(self, permiso):
        """
        Metodo que verifica si un Rol tiene un permiso de proyecto.

        :param permiso:
        :return:
        """
        return self.permisos.filter(codename=permiso).exists()

    def get_pp_por_proyecto(self):
        """
        Metodo que retorna todos los permisos de proyecto que son aplicables al proyecto en general
        asignados a un Rol de Proyecto.

        Retorna:
            QuerySet: QuerySet con todos los permisos aplicables a nivel de Proyecto.
        """
        return self.permisos.filter(codename__startswith='pp_').filter(codename__regex=r'pp_[^f_]')

    def get_pp_por_fase(self):
        """
        Metodo que retorna todos los permisos de proyecto que son aplicables solo dentro de una fase de un proyecto.

        Retorna:
            QuerySet: QuerySet con todos los permisos aplicables dentro de una fase de un Proyecto
        """
        return self.permisos.filter(codename__startswith='pp_f_')


class PermisosPorFase(models.Model):
    """
    Modelo que representa la relacion entre una fase de un Proyecto y los Permisos de Proyecto asignados
    a un Participante de un Proyecto.
    """
    fase = models.ForeignKey('gestion_de_fase.Fase', on_delete=models.CASCADE)
    permisos = models.ManyToManyField(Permission)

    def __str__(self):
        return f'{self.fase}: {self.permisos}'

    def get_permisos(self):
        """
        TODO: falta comentar
        :return:
        """
        return self.permisos.all()

    def asignar_permisos_de_proyecto(self, permisos):
        """
        Metodo que recibe como parametro una lista de permisos a asignar a un usuario en una fase.

        Args:
            permisos: lista de Permisos de Proyecto a asignar al Rol.
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
        """
        Metodo que verifica si el objeto PermisoPorFase tiene un determinado Permiso de Proyecto

        Args:
            permiso: codename de Permiso de Proyecto.

        Retorna:
            True si el objeto PermisoPorFase tiene el Permiso de Proyecto.\n
            False en caso contrario.
        """
        return self.permisos.filter(codename=permiso).exists()
