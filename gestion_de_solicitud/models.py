from django.db import models
from django.utils import timezone

from gestion_de_proyecto.models import Participante
from gestion_de_item.models import Item
from gestion_linea_base.models import LineaBase


class EstadoSolicitud:
    PENDIENTE = 'Pendiente'
    APROBADA = 'Aprobada'
    RECHAZADA = 'Rechazada'


class SolicitudDeCambio(models.Model):
    """
    Modelo que guarda información de una solicitud de cambio.


    """
    solicitante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    linea_base = models.ForeignKey(LineaBase, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=500)
    fecha = models.DateTimeField(default=timezone.now)
    numero_de_miembros = models.IntegerField()
    estado = models.CharField(max_length=30)

    def get_items_a_modificar(self):
        """
        TODO: Marcelo Comentar
        :return:
        """
        return self.asignacion_set.all()


class Asignacion(models.Model):
    """
    Modelo que representa un item y el usuario al que fue asignado dentro de una solicitud de cambio.
    """
    usuario = models.ForeignKey(Participante, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    solicitud = models.ForeignKey(SolicitudDeCambio, on_delete=models.CASCADE)
    motivo = models.CharField(max_length=500)


class Voto(models.Model):
    """
    Modelo que maneja el voto de un miembro de de comite
    """
    miembro = models.ForeignKey(Participante, on_delete=models.CASCADE)
    voto_a_favor = models.BooleanField()
    solicitud = models.ForeignKey(SolicitudDeCambio, on_delete=models.CASCADE)
