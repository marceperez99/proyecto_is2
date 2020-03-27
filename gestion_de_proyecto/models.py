from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from gestion_de_fase.models import Fase
from roles_de_proyecto.models import PermisosPorFase


class EstadoDeProyecto:
    """
        Clase que se usa para facilitar el nombramiento de los estados del proyecto.\n
        Estados de Proyecto:\n
        CONFIGURACION = En Configuracion\n
        INICIADO = Iniciado\n
        FINALIZADO = Finalizado\n
        CANCELADO = Finalizado\n
    """
    CONFIGURACION = "En Configuración"
    INICIADO = "Iniciado"
    FINALIZADO = "Finalizado"
    CANCELADO = "Finalizado"


class Proyecto(models.Model):
    """
        Modelo para la clase proyecto
    """
    nombre = models.CharField(max_length=101)
    descripcion = models.CharField(max_length=401)
    gerente = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    creador = models.ForeignKey(User, related_name='proyectos_creador', on_delete=models.CASCADE, null=True)
    fecha_de_creacion = models.DateTimeField(verbose_name="Fecha de Creacion",default=timezone.now)
    estado = models.CharField(max_length=20, verbose_name="Estado del Proyecto")

    class Meta:
        permissions = [('ps_crear_pry', 'Crear Proyecto'),
                       ('ps_cancelar_pry', 'Cancelar Proyecto'),
                       ('ps_ver_pry', 'Visualizar lista de todos los Proyectos guardados en el Sistema')]

    def __str__(self):
        return self.nombre

    def get_participante(self, usuario):
        """
        Metodo que retorna el objeto Participante asociado al proyecto y que contenga el usuario
        pasado como parametro.\n
        Args:\n
            usuario: objeto User\n
        Retorna:\n
            Participante

        """
        return self.participante_set.get(usuario=usuario)

    def get_gerente(self):
        """
        Metodo que retorna el objeto User del gerente del Proyecto

        Retorna:
            User: gerente del Proyecto.
        """
        return self.gerente

    def get_participantes(self):
        """
        Metodo que retorna todos los participantes del proyecto.\n
        Retorna:\n
            QuerySet: objeto con todos los participantes del Proyecto.
        """
        return self.participante_set.all()

    def get_fases(self):
        """
        Metodo que retorna todas las fases del Proyecto en orden
        segun el campo fase_anterior.\n
        Retorna:\n
            Lista: lista de fases del proyecto en orden
        """
        ultima_fase = Fase.objects.all().filter(fase__isnull=True)[0]
        lista = []
        while ultima_fase is not None:
            lista.insert(0, ultima_fase)
            ultima_fase = ultima_fase.fase_anterior
        return lista

    def asignar_rol_de_proyecto(self, usuario, rol, permisos_por_fase):
        """
        Metodo que asigna a un participante un rol de proyecto y un conjunto de permisos por cada fase del
        proyecto.

        Args:
            rol: RolDeProyecto, rol a asignar al usuario.\n
            usuario: User, usuario a quien se asignara el rol.\n
            permisos_por_fase: Diccionario con las fases del proyecto y el conjunto de permisos de proyecto
            a asignar al usuario en cada fase respectivamente.
        """
        participante = self.get_participante(usuario)
        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)

    def tiene_permiso_de_proyecto(self, usuario, permiso):
        """
        Metodo que verifica si un usuario tiene o no un determinado permiso de proyecto \n
        Args:\n
        usuario: User\n
        permiso: codename(string) del permiso de proyecto\n
        Retorna:\n
            True si el usuario tiene el permiso de proyecto.\n
            False en caso contrario.\n
        """
        return self.get_participante(usuario).tiene_pp(permiso)

    def tiene_permiso_de_proyecto_en_fase(self, usuario, fase, permiso):
        """
        Metodo que retorna True si el usuario tiene un determinado permiso de proyecto dentro de una determinada
        fase.\n
        Args:
            usuario: User\n
            fase: Fase\n
            permiso: codename(string) del permiso de proyecto\n
        Retorna:
            True si el usuario tiene el permiso dentro de la fase del proyecto.\n
            False en caso contrario.
        """
        return self.get_participante(usuario).tiene_pp_por_fase(fase, permiso)


class Participante(models.Model):
    """
    Modelo que representa la relacion entre un usuario del sistema y un proyecto en particular.\n
    Atributos:
        - proyecto: Proyecto
        - usuario: User
        - rol: RolDeProyecto
    """
    proyecto = models.ForeignKey('gestion_de_proyecto.Proyecto', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    rol = models.ForeignKey('roles_de_proyecto.RolDeProyecto', null=True, on_delete=models.CASCADE)
    permisos_por_fase = models.ManyToManyField('roles_de_proyecto.PermisosPorFase')

    class Meta:
        permissions = [
            ('pp_agregar_participante', 'Agregar Participante al Proyecto'),
            ('pp_eliminar_participante', 'Eliminar Participante del Proyecto'),
            ('pp_asignar_rp_a_participante', 'Asignar Rol de Proyecto a Participante'),
            ('pp_desasignar_rp_a_participante', 'Desasignar Rol de Proyecto a Participante'),
        ]

    def asignar_permisos_de_proyecto(self, permisos_por_fase):
        """
        Metodo que asigna a un participante de un proyecto un conjunto de permisos por cada fase del proyecto.

        Args:
            permisos_por_fase: Diccionario que contiene por cada fase, una lista de permisos de proyecto.

        Lanza:
            Exception: si las claves del diccionario recibido no son del tipo string o del tipo Fase.
        """
        for fase in permisos_por_fase.keys():
            if isinstance(fase, str):
                fase_obj = Fase.objects.get(id=fase)
            elif isinstance(fase, Fase):
                fase_obj = fase
            else:
                raise Exception('Objeto recibido no valido')

            pp_por_fase = PermisosPorFase(fase=fase_obj)
            pp_por_fase.save()
            pp_por_fase.asignar_permisos_de_proyecto(permisos_por_fase[fase])
            self.permisos_por_fase.add(pp_por_fase)

    def asignar_rol_de_proyecto(self, rol, permisos_por_fase={}):
        """
        Metodo que asigna a un participante un rol de proyecto y un conjunto de permisos por cada fase del proyecto

        Args:
            rol: RolDeProyecto, rol a asignar al usuario.\n
            permisos_por_fase: Diccionario que contiene por cada fase, una lista de permisos de proyecto.

        """
        if permisos_por_fase != {}:
            self.asignar_permisos_de_proyecto(permisos_por_fase)
        self.rol = rol
        self.save()

    def tiene_rol(self):
        """
        Metodo que verifica si el participante tiene asignado un rol de Proyecto

        Retorna:
            True si el participante cuenta con un rol asignado.\n
            False en caso contrario.
        """
        assert (self.rol is None and not self.permisos_por_fase.all().exists()) or (self.rol is not None)
        return self.rol is not None

    def tiene_pp(self, permiso):
        """
        Metodo que comprueba si el participante tiene un Permiso de Proyecto.

        Args:
            permiso: codename(string) del permiso de proyecto.

        Retorna:
            True si el usuario cuenta con el permiso de proyecto.\n
            False en caso contrario.
        """
        return self.proyecto.get_gerente().id == self.usuario.id or (self.tiene_rol() and self.rol.tiene_pp(permiso))

    def tiene_pp_en_fase(self, fase, permiso):
        """
        Metodo que comprueba si el participante tiene un Permiso de Proyecto dentro de una determinada fase.

        Args:
            fase: identificador(int) de la fase o objeto Fase.\n
            permiso: codename(string) del permiso de proyecto.

        Retorna:
            True si el usuario cuenta con el permiso de proyecto.\n
            False en caso contrario.
        """
        if not self.tiene_rol():
            return False
        if isinstance(fase, int):
            fase = Fase.objects.get(id=fase)
        if isinstance(fase, Fase):
            return self.pp_por_fase.get(fase=fase).tiene_pp(permiso)
        else:
            raise Exception('Tipo de objecto fase inadecuado')
