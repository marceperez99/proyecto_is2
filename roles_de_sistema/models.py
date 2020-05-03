from django.contrib.auth.models import Permission, Group
from django.db import models


class RolDeSistema(models.Model):
    """
    Clase un Rol de Sistema dentro del sistema. Esta clase sirve además como modelo para la creación de la Base de
    Datos.

    Clase Padre:
        models.Model

    Atributos:
        nombre: models.CharField \n
        descripcion: models.CharField \n
        permisos: models.ManyToManyField, representa la relacion de un rol con los permisos que incluye.
    """
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=200)
    permisos = models.ManyToManyField(Permission)
    #creador = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ('pa_crear_proyecto', 'Crear Proyecto'),
            ('pa_cancelar_proyecto', 'Cancelar Proyecto'),
            ('ps_ver_proyecto', 'Visualizar lista de todos los Proyectos guardados en el Sistema'),
            ('ps_ver_rs', 'Visualizar Lista de Roles de Sistema'),
            ('pa_crear_rs', 'Crear nuevo Rol de Sistema'),
            ('pa_eliminar_rs', 'Eliminar Rol de Sistema'),
            ('pa_asignar_rs', 'Asignar Rol de Sistema'),
            ('pa_desasignar_rs', 'Desasignar Rol de Sistema'),
            ('pa_editar_rs', 'Editar Rol de Sistema'),
            ('pa_crear_rp', 'Crear Rol de Proyecto'),
            ('ps_ver_rp', 'Visualizar Lista de Roles de Proyecto'),
            ('pa_eliminar_rp', 'Eliminar Rol de Proyecto'),
            ('pa_editar_rp', 'Editar Rol de Proyecto'),
            ('ps_ver_usuarios', 'Visualizar lista de todos los Usuarios registrados en el Sistema'),
            ('pa_desactivar_usuario', 'Desactiva a un Usuario del Sistema'),
            ('pa_config_cloud', 'Configurar Conexión con el servicio de almacenamiento en la nube'),
            ('pa_config_sso', 'Configurar Conexión con SSO'),
            ('pu_acceder_sistema', 'Acceder al Sistema'),
        ]

    def save(self, *args, **kwargs):
        """
        Metodo que se encarga de, si es un nuevo Rol de Sistema, guardar el nuevo Rol de Sistema, y sino , guardar los
        cambios del Rol ya existente

        Retorna:
            void
        """
        super(RolDeSistema, self).save(*args, **kwargs)
        if Group.objects.filter(name=self.nombre).exists():
            group = Group.objects.get(name=self.nombre)
            group.permissions.clear()
        else:
            group = Group(name=self.nombre)
            group.save()

        group.permissions.add(Permission.objects.get(codename='pu_acceder_sistema'))

        for permiso in self.permisos.all():
            group.permissions.add(permiso)

    def __str__(self):
        return self.nombre

    def get_permisos(self):
        """
        Metodo que retorna una lista de todos los permisos que incluye este Rol de Sistema.

        Retorna:
            lista de Permission
        """
        return [p for p in self.permisos.all()]

    def es_utilizado(self):
        """
        Metodo que retorna True si existe algun usuario utilizando este Rol de Sistema en algun Sistema,
        False en caso contrario.

        Retorna:
            Booleano
        """
        group = Group.objects.get(name=self.nombre)
        return group.user_set.all().exists()

    def eliminar_rs(self):
        """
        Metodo que retorna True si el rol d sistema fue eliminado con exito, False en caso contrario

        Retorna:
            Booleano
        """
        group = Group.objects.get(name=self.nombre)
        if self.es_utilizado():
            return False
        else:
            group.delete()
            self.delete()
            return True
