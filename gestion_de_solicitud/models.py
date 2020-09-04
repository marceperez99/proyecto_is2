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

    def __str__(self):
        return f'Solicitud de Ruptura de Linea Base {self.linea_base}'

    def get_items_a_modificar(self):
        """
        TODO: Marcelo Comentar
        :return:
        """
        return self.asignacion_set.all()

    def get_proyecto(self):
        return self.linea_base.get_proyecto()

    def ya_voto(self, participante):
        return self.voto_set.filter(miembro=participante).exists()

    def get_votos_a_favor(self):
        #TODO MARCELO
        return self.voto_set.filter(voto_a_favor=True).count()

    def get_votos_en_contra(self):
        # TODO MARCELO
        return self.voto_set.filter(voto_a_favor=False).count()

    def get_numero_de_votos(self):
        # TODO MARCELO
        return self.voto_set.all().count()

    def get_numero_de_votos_faltantes(self):
        # TODO MARCELO
        comite = self.linea_base.get_proyecto().get_comite_de_cambios()
        return comite.miembros.all().count() - self.get_numero_de_votos()

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
