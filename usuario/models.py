from django.contrib.auth.models import User, Group

# Create your models here.
from gestion_de_proyecto.models import Participante, Proyecto, EstadoDeProyecto
from roles_de_sistema.models import RolDeSistema


class Usuario(User):
    """
    Modelo proxy que extiende el modelo User de Django.

    """
    class Meta:
        proxy = True

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def asignar_rol_a_usuario(self, rs_id):
        self.groups.clear()
        rs = RolDeSistema.objects.get(id=rs_id)
        group = Group.objects.get(name=rs.nombre)
        self.groups.add(group)

    def desasignar_rol_a_usuario(self):
        flag = True
        if not self.get_proyectos():
            self.groups.clear()
        else:
            flag = False
        return flag

    def tiene_rs(self):
        return self.groups.all().exists()

    def es_administrador(self):
        return self.groups.filter(name='Administrador').exists()

    def get_rol_de_sistema(self):
        """
        Metodo que retorna el rol de Sistema que tiene asignado el usuario.

        Retorna:
            RolDeSistema: objeto con los datos del rol de sistema asignado al usuario.
        """
        assert self.groups.all().count() in [0, 1], 'El usuario tiene mas de un rol de sistema asignado'
        if self.groups.all().count() == 1:
            rol = self.groups.all()[0]
            return RolDeSistema.objects.get(nombre=rol.name)
        return None

    def get_permisos_list(self):
        """
        Metodo que retorna una lista con los codename de los permisos de sistema que tiene el usuario.\n
        Retorna:
            list(): lista con los permisos de sistema del usuario.
        """
        if self.groups.all().exists():
            return [ps.codename for ps in self.groups.all()[0].permissions.all()]
        else:
            return []

    def get_proyectos(self):
        """
        Método que retorna la lista de proyectos en los que el usuario participa.

        Retorna:
            proyectos: lista[] con los proyectos en los que el usuario participa.
        """
        user = User.objects.get(id = self.id)

        proyectos = []
        proyectos_set = Proyecto.objects.filter(gerente = user)
        for proyecto in proyectos_set:
            proyectos.append(proyecto)
        participantes = Participante.objects.filter(usuario = user).exclude(rol = None)
        for participante in participantes:
            proyectos.append(participante.proyecto)

        return proyectos

    def get_proyectos_activos(self):
        """
        Metodo que retorna la lista de Proyectos Iniciados, y los proyectos En Configuracion
        , en los que participa un Usuario.

        Retorna:
            list(): Lista de Proyectos en los participa el usuario
        """
        proyectos = list(Proyecto.objects.filter(gerente=self)
                         .exclude(estado=EstadoDeProyecto.CANCELADO).exclude(estado=EstadoDeProyecto.FINALIZADO))

        participantes = Participante.objects.filter(usuario=self).exclude(rol=None)
        for participante in participantes:
            if participante.proyecto.estado == EstadoDeProyecto.INICIADO:
                proyectos.append(participante.proyecto)

        return proyectos
