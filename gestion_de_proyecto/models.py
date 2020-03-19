from django.db import models
from django.contrib.auth.models import User
from roles_de_proyecto.models import RolDeProyecto
# Create your models here.


class EstadoDeProyecto():
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

class Participante(models.Model):
    """

    Modelo que relaciona describe un usuario como participante de un proyecto y su rol dentro de este

    Atributos:
        - proyecto: Proyecto
        - usuario: User
        - rol: RolDeProyecto
    """
    proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    rol = models.ForeignKey(RolDeProyecto,on_delete=models.CASCADE)

