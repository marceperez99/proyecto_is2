from django.contrib.auth.models import User, Permission
from django.db import models
from django.utils import timezone

from gestion_de_fase.models import Fase
from roles_de_proyecto.models import PermisosPorFase


class EstadoDeProyecto:
    """
    Clase que se usa para facilitar el nombramiento de los estados del proyecto.

    Estados de Proyecto:
        CONFIGURACION = En Configuracion \n
        INICIADO = Iniciado \n
        FINALIZADO = Finalizado \n
        CANCELADO = Cancelado
    """
    CONFIGURACION = "En Configuración"
    INICIADO = "Iniciado"
    FINALIZADO = "Finalizado"
    CANCELADO = "Cancelado"


class Proyecto(models.Model):
    """
        Modelo para la clase proyecto
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=400)
    gerente = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    creador = models.ForeignKey(User, related_name='proyectos_creador', on_delete=models.CASCADE, null=True)
    fecha_de_creacion = models.DateTimeField(verbose_name="Fecha de Creacion", default=timezone.now)
    estado = models.CharField(max_length=20, verbose_name="Estado del Proyecto")

    def __str__(self):
        return self.nombre

    def get_participante(self, usuario):
        """
        Metodo que retorna el objeto Participante asociado al proyecto y que contenga el usuario
        pasado como parametro.

        Argumentos:
            usuario: User

        Retorna:
            Participante
        """
        if self.gerente.id == usuario.id:
            return self.participante_set.get(usuario=usuario)
        else:
            if self.participante_set.filter(usuario=usuario, rol__isnull=False).exists():
                return self.participante_set.get(usuario=usuario, rol__isnull=False)
            else:
                return None

    def get_gerente(self):
        """
        Metodo que retorna el objeto User del gerente del Proyecto

        Retorna:
            User: gerente del Proyecto.
        """
        return self.gerente

    def get_participantes(self):
        """
        Metodo que retorna todos los participantes del proyecto.

        Retorna:
            QuerySet: objeto con todos los participantes del Proyecto.
        """
        participantes = [self.participante_set.get(usuario=self.gerente)]
        participantes.extend(list(self.participante_set.all().filter(rol__isnull=False)))

        return participantes

    def get_comite_de_cambios(self):
        """
        Metodo que retorna el Comite de Cambios asociado al Proyecto.

        Retorna:
             Comite: objeto Comite del proyecto
        """
        assert self.comite_set.all().count() == 1, 'El Proyecto no tiene un Comite asociado'
        return self.comite_set.all()[0]

    def get_fases(self):
        """
        Metodo que retorna todas las fases del Proyecto en orden, segun el campo fase_anterior.

        Retorna:
            Lista: lista de fases del proyecto en orden
        """
        lista = []
        if self.fase_set.all().filter(fase__isnull=True).exists():
            ultima_fase = self.fase_set.all().filter(fase__isnull=True)[0]
            while ultima_fase is not None:
                lista.insert(0, ultima_fase)
                ultima_fase = ultima_fase.fase_anterior
        return lista

    def asignar_rol_de_proyecto(self, usuario, rol, permisos_por_fase):
        """
        Metodo que asigna a un participante un rol de proyecto y un conjunto de permisos por cada fase del
        proyecto.

        Argumentos:
            rol: RolDeProyecto, rol a asignar al usuario.\n
            usuario: User, usuario a quien se asignara el rol.\n
            permisos_por_fase: Diccionario con las fases del proyecto y el conjunto de permisos de proyecto
            a asignar al usuario en cada fase respectivamente.
        """
        assert self.participante_set.filter(
            usuario=usuario).exists() is True, 'No existe el participante en el proyecto'
        participante = self.participante_set.get(usuario=usuario)
        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)

    def tiene_permiso_de_proyecto(self, usuario, permiso):
        """
        Metodo que verifica si un usuario tiene o no un determinado permiso de proyecto

        Argumentos:
            usuario: User \n
            permiso: codename(string) del permiso de proyecto

        Retorna:
            True si el usuario tiene el permiso de proyecto.\n
            False en caso contrario.
        """
        return self.get_participante(usuario).tiene_pp(permiso)

    def tiene_permiso_de_proyecto_en_fase(self, usuario, fase, permiso):
        """
        Metodo que retorna True si el usuario tiene un determinado permiso de proyecto dentro de una determinada
        fase.

        Argumentos:
            usuario: User\n
            fase: Fase\n
            permiso: codename(string) del permiso de proyecto

        Retorna:
            True si el usuario tiene el permiso dentro de la fase del proyecto.\n
            False en caso contrario.
        """
        participante = self.get_participante(usuario)
        if participante is None:
            return False
        else:
            return participante.tiene_pp_en_fase(fase, permiso)

    def cancelar(self):
        """
        Metodo de la clase proyecto que verifica si un proyecto no este en en estado finalizado,
        si este se encuentra en otro estado, lo pone en estado "Cancelado".

        Argumentos:
            proyecto: Proyecto

        Retorna:
            True: si el proyecto se encuentra en estado "En Configuracion" o "iniciado".\n
            False: si el proyecto ya se encuentra en estado "Finalizado".
        """
        if self.estado == EstadoDeProyecto.FINALIZADO:
            return False
        else:
            self.estado = EstadoDeProyecto.CANCELADO
        return True

    def iniciar(self):
        """
        Metodo de la clase proyecto, que verifica si este tiene al menos una fase, si esta la tiene
        cambia su estado de "En Configuracion" a "Iniciado"

        Lanza:
            Exception: si el el proyecto no tiene fases creadas.\n
            Exception: si aun no se ha definido un Comite de Cambios.
        """
        if not self.fase_set.exists():
            raise Exception("El proyecto no cuenta con ninguna Fase creada")
        comite = Comite.objects.get(proyecto=self)
        numero_de_miembros = comite.miembros.all().count()
        if numero_de_miembros <= 1:
            raise Exception('El Proyecto no cuenta con un Comite de Cambios definido.')
        if numero_de_miembros % 2 == 0:
            raise Exception('El numero de usuarios que conforman el Comite de Cambios debe ser impar.')

        self.estado = EstadoDeProyecto.INICIADO
        self.save()

    def eliminar_participante(self, usuario):
        """
        Método que permite eliminar un participante de un proyecto.
        Realiza un borrado lógico asignandole un valor nulo al rol de este participante

        Argumentos:
            usuario: User usuario al que se desea desvincular de un proyecto.

        Retorna:
            None
        """
        if self.participante_set.filter(usuario=usuario, rol__isnull=False).exists():
            mensaje = "El sistema es inconsistente: 2 participantes activos hacen referencia al mismo usuario."
            assert len(self.participante_set.filter(usuario=usuario, rol__isnull=False)) == 1, mensaje
            participante = self.participante_set.get(usuario=usuario, rol__isnull=False)
            participante.rol = None
            participante.save()


class Participante(models.Model):
    """
    Modelo que representa la relacion entre un usuario del sistema y un proyecto en particular.

    Atributos:
        - proyecto: Proyecto \n
        - usuario: User \n
        - rol: RolDeProyecto
    """
    proyecto = models.ForeignKey('gestion_de_proyecto.Proyecto', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    rol = models.ForeignKey('roles_de_proyecto.RolDeProyecto', null=True, on_delete=models.CASCADE)
    permisos_por_fase = models.ManyToManyField('roles_de_proyecto.PermisosPorFase')

    def __str__(self):
        return self.usuario.get_full_name()

    def get_rol_nombre(self):
        """
        Metodo que retorna el nombre del Rol de Proyecto que tiene asignado un participante dentro del Proyecto.

        Retorna:
            - string: nombre del rol de Proyecto que tiene asignado el usuario dentro del proyecto, \n
            - retorna 'Gerente de Proyecto' si el participante es el Gerente de este proyecto.
        """
        if self.rol is not None:
            return self.rol.nombre
        else:
            return 'Gerente de Proyecto' if self.usuario == self.proyecto.gerente else None

    def get_pp_por_fase(self):
        """
        Metodo que retorna un diccionario que, por cada fase del proyecto, contiene una lista de los permisos de
        proyecto que el usuario tiene asignado en la fase correspondiente.

        Retorna:

            - dict: diccionario con la estructura.
                    { Fase: [Permission, ...] }
        """
        pp_por_fase = {}
        for fase in self.proyecto.get_fases():
            if self.permisos_por_fase.filter(fase=fase).exists():
                pp_por_fase[fase] = self.permisos_por_fase.get(fase=fase).permisos.all()
            else:
                pp_por_fase[fase] = []

        return pp_por_fase

    def asignar_permisos_de_proyecto(self, permisos_por_fase):
        """
        Metodo que asigna a un participante de un proyecto un conjunto de permisos por cada fase del proyecto.

        Argumentos:
            - permisos_por_fase: Diccionario que contiene por cada fase, una lista de permisos de proyecto.

        Retorna:
            - Exception: si las claves del diccionario recibido no son del tipo string o del tipo Fase.
        """
        for fase in permisos_por_fase.keys():
            if isinstance(fase, str):
                fase_obj = Fase.objects.get(id=fase)
            elif isinstance(fase, Fase):
                fase_obj = fase
            else:
                raise Exception('Objeto recibido no valido')

            if permisos_por_fase[fase]:
                pp_por_fase = PermisosPorFase(fase=fase_obj)
                pp_por_fase.save()
                pp_por_fase.asignar_permisos_de_proyecto(permisos_por_fase[fase])
                self.permisos_por_fase.add(pp_por_fase)

    def asignar_rol_de_proyecto(self, rol, permisos_por_fase={}):
        """
        Metodo que asigna a un participante un rol de proyecto y un conjunto de permisos por cada fase del proyecto

        Argumentos:
            - rol: RolDeProyecto, rol a asignar al usuario.\n
            - permisos_por_fase: Diccionario que contiene por cada fase, una lista de permisos de proyecto.
        """
        self.permisos_por_fase.clear()
        if permisos_por_fase != {}:
            self.asignar_permisos_de_proyecto(permisos_por_fase)
        self.rol = rol
        self.save()

    def tiene_rol(self):
        """
        Metodo que verifica si el participante tiene asignado un rol de Proyecto

        Retorna:
            - True si el participante cuenta con un rol asignado.\n
            - False en caso contrario.
        """
        assert (self.rol is None and not self.permisos_por_fase.all().exists()) or (self.rol is not None)
        return self.usuario == self.proyecto.gerente or self.rol is not None

    def tiene_pp(self, permiso):
        """
        Metodo que comprueba si el participante tiene un Permiso de Proyecto.

        Argumentos:
            - permiso: codename(string) del permiso de proyecto.

        Retorna:
            - True si el usuario cuenta con el permiso de proyecto.\n
            - False en caso contrario.
        """
        return self.proyecto.get_gerente().id == self.usuario.id or (self.tiene_rol() and self.rol.tiene_pp(permiso))

    def tiene_pp_en_fase(self, fase, permiso):
        """
        Metodo que comprueba si el participante tiene un Permiso de Proyecto dentro de una determinada fase.

        Argumentos:
            - fase: identificador(int) de la fase o objeto Fase.\n
            - permiso: codename(string) del permiso de proyecto.

        Retorna:
            - True si el usuario cuenta con el permiso de proyecto.\n
            - False en caso contrario.
        """
        if not self.tiene_rol():
            return False
        if self.usuario.id == self.proyecto.gerente.id:
            return True
        if isinstance(fase, int):
            fase = Fase.objects.get(id=fase)
        if isinstance(fase, Fase):
            return self.permisos_por_fase.filter(fase=fase).exists() and self.permisos_por_fase.get(fase=fase).tiene_pp(
                permiso)
        else:
            raise Exception('Tipo de objecto fase inadecuado')

    def get_permisos_de_proyecto_list(self):
        """
        Metodo que retorna una lista con los codenames de los permisos que tiene asignado un participante
        del proyecto, este metodo solo retorna los permisos de proyecto que le permite realizar operaciones
        dentro del proyecto, no los permisos que tiene el usuario dentro de las fases.

        Retorna:
            - list(): Lista de codenames de Permisos de Proyecto.
        """
        if self.usuario == self.proyecto.gerente:
            permisos_de_proyecto = list(Permission.objects.all().filter(codename__startswith='pp_')
                                        .exclude(codename__startswith='pp_f'))
            permisos_de_proyecto += list(Permission.objects.all().filter(codename__startswith='pg_')
                                         .exclude(codename__startswith='pg_f'))
            permisos_de_proyecto += list(Permission.objects.all().filter(codename__startswith='pu_')
                                         .exclude(codename__startswith='pu_f'))

            return [pp.codename for pp in permisos_de_proyecto],
        else:
            return [pp.codename for pp in self.rol.get_pp_por_proyecto()]

    def get_permisos_por_fase_list(self, fase):
        """
        Metodo que retorna los permisos de proyecto que tiene un participante dentro de una determinada
        fase de un proyecto.

        Argumentos:
            - fase: Fase

        Retorna:
            - list(): Lista de codenames de Permisos de Proyecto.
        """
        if self.usuario.id == self.proyecto.gerente.id:
            permisos_por_fase = list(Permission.objects.filter(codename__startswith='pu_f_'))
            permisos_por_fase += list(Permission.objects.filter(codename__startswith='pp_f_'))
            permisos_por_fase += list(Permission.objects.filter(codename__startswith='pg_f_'))

        else:
            if self.permisos_por_fase.filter(fase=fase).exists():
                permisos_por_fase = self.permisos_por_fase.get(fase=fase).get_permisos()
            else:
                permisos_por_fase = []
        return [pp.codename for pp in permisos_por_fase]


class Comite(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    miembros = models.ManyToManyField(Participante)

    def es_miembro(self, participante):
        if self.miembros.filter(id=participante.id).exists():
            return True
        else:
            return False
