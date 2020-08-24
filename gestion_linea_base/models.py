from django.db import models
from gestion_de_item.models import Item


class EstadoLineaBase:
    COMPROMETIDA = 'Comprometida'
    ROTA = 'Rota'
    CERRADA = 'CERRADA'


class LineaBase(models.Model):
    # TODO: Marcos, documentar.
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=40)
    items = models.ManyToManyField(Item)

    def __str__(self):
        return self.nombre
