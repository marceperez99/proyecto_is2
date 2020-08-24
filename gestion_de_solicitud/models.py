from django.db import models
from usuario.models import Usuario
from gestion_de_item.models import Item
from gestion_linea_base.models import LineaBase
# Create your models here.

class SolicitudDeCambio(models.odel):
    solicitante = models.ForeignKey(Usuario)
    linea_base = models.ForeignKey(LineaBase)
    descripcion = models.CharField(max_length=500)
    fecha = models.DateTimeField()
    numero_de_miembros = models.IntegerField()
    votos_a_favor = models.IntegerField(default=0)

class Asignacion(models.model):
    usuario = models.ForeignKey(Usuario)
    item = models.ForeignKey(Item)
    solicitud = models.ForeignKey(SolicitudDeCambio)