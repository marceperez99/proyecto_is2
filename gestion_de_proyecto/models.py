from django.db import models
from django.contrib.auth.models import User
from roles_de_proyecto.models import RolDeProyecto, PermisosPorFase


# Create your models here.


class EstadoDeProyecto:
    """
        Clase que se usa para facilitar el nombramiento de los estados del proyecto
    """
    CONFIGURACION = "En Configuracion"
    INICIADO = "Iniciado"
    FINALIZADO = "Finalizado"
    CANCELADO = "Finalizado"


class Proyecto(models.Model):
    """
        Modelo para la clase proyecto
    """
    nombre = models.CharField(max_length=15)
    descripcion = models.CharField(max_length=50)
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    fechaCreacion = models.DateField(verbose_name="Fecha de Creacion")
    estado = models.CharField(max_length=20, verbose_name="Estado del Proyecto")

    def get_participante(self, usuario):
        """
        TODO
        :param usuario:
        :return:
        """
        return self.participante_set.get(usuario=usuario)

    def get_participantes(self):
        """
        TODO
        :return:
        """
        return self.participante_set.all()

    def get_fases(self):
        """
        TODO
        :return:
        """
        return self.fase_set.all()

    def asignar_rol_de_proyecto(self, usuario, rol, permisos_por_fase):
        """
        TODO
        :param rol:
        :param usuario:
        :param permisos_por_fase:
        :return:
        """
        participante = self.get_participante(usuario)
        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)

    def tiene_permiso_de_proyecto(self, usuario, permiso):
        """
        Metodo que comprueba que dado un participante del proyecto y un permiso de proyecto, verifique que el usuario
        tenga dicho permiso.
        :param usuario:
        :param permiso:
        :return:
        """
        return self.get_participante(usuario).tiene_pp(permiso)

    def tiene_permiso_de_proyecto_en_fase(self, usuario, fase, permiso):
        """
        Metodo que retorna True si el usuario tiene un determinado permiso de proyecto dentro de una determinada fase.
        :param usuario:
        :param fase:
        :param permiso:
        :return:
        """
        return self.get_participante(usuario).tiene_pp_por_fase(fase, permiso)


class Participante(models.Model):
    """
    Modelo que relaciona describe un usuario como participante de un proyecto y su rol dentro de este

    Atributos:
        - proyecto: Proyecto
        - usuario: User
        - rol: RolDeProyecto
    """
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(RolDeProyecto, null=True, on_delete=models.CASCADE)
    permisos_por_fase = models.ManyToManyField(PermisosPorFase)

    class Meta:
        permissions = [
            ('pp_agregar_participante', 'Agregar Participante al Proyecto'),
            ('pp_eliminar_participante', 'Eliminar Participante del Proyecto'),
            ('pp_asignar_rp_a_participante', 'Asignar Rol de Proyecto a Participante'),
            ('pp_desasignar_rp_a_participante', 'Desasignar Rol de Proyecto a Participante'),
        ]

    def asignar_rol_de_proyecto(self, rol, permisos_por_fase):
        """
        Metodo que asigna a un participante de un proyecto un conjunto de permisos
        :param rol:
        :param permisos_por_fase:
        :return:
        """
        for fase in permisos_por_fase.keys():
            pp_por_fase = PermisosPorFase(fase=fase)
            pp_por_fase.save()
            pp_por_fase.asignar_permisos_de_proyecto(permisos_por_fase[fase])
            self.permisos_por_fase.add(pp_por_fase)
        self.rol = rol
        self.save()

    def tiene_pp(self, permiso):
        """
        Metodo que retorna True
            TODO
        :param permiso:
        :return:
        """
        return self.rol.tiene_pp(permiso)

    def tiene_pp_en_fase(self, fase, permiso):
        """TODO"""
        return self.pp_por_fase.get(fase=fase).tiene_pp(permiso)
