from django.db import models

# Create your models here.

class Fase(models.Model):
    """
        Modelo para la clase Fase
    """
    nombre = models.CharField(max_length=15)
    items = models.ForeignKey('Item', on_delete=models.CASCADE)
    lineaBase = models.ForeignKey('LineaBase', on_delete=models.CASCADE, verbose_name="Linea Base")
    faseCerrada = models.BooleanField(verbose_name="Fase Cerrada")
    puedeCerrarse = models.BooleanField(verbose_name="Puede Cerrarse")