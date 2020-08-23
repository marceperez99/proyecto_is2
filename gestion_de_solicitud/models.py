from django.db import models
from usuario.models import Usuario
from gestion_de_item.models import Item
from gestion_linea_base.models import LineaBase
# Create your models here.


class SolicitudDeCambio(models.Model):
    """
    Modelo que guarda información de una solicitud de cambio.


    """
    solicitante = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    linea_base = models.ForeignKey(LineaBase,on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=500)
    fecha = models.DateTimeField()
    numero_de_miembros = models.IntegerField()

class Asignacion(models.Model):
    """
    Modelo que representa un item y el usuario al que fue asignado dentro de una solicitud de cambio.
    """
    usuario = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    solicitud = models.ForeignKey(SolicitudDeCambio,on_delete=models.CASCADE)

class Voto(models.Model):
    """
    Modelo que maneja el voto de un miembro de de comite
    """
    miembro = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    voto_a_favor = models.BooleanField()
    solicitud = models.ForeignKey(SolicitudDeCambio,on_delete=models.CASCADE)