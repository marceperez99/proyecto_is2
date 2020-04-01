from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
from gestion_de_proyecto.models import Participante, Proyecto
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
        if self.groups.all().exists():
            self.groups.all().delete()
        rs = RolDeSistema.objects.get(id=rs_id)
        print(rs.nombre)
        group = Group(name=rs.nombre)
        group.save()
        self.groups.add(group)

    def get_rol_de_sistema(self):
        """
        Metodo que retorna el rol de Sistema que tiene asignado el usuairo.

        Retorna:
            RolDeSistema: objeto con los datos del rol de sistema asignado al usuario.
        """
        assert self.groups.all().count() in [0, 1], 'El usuario tiene mas de un rol de sistema asignado'
        if self.groups.all().count() == 1:
            rol = self.groups.all()[0]
            return RolDeSistema.objects.get(nombre=rol.name)
        return None

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
