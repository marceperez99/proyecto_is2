from django.db import models

class Fase(models.Model):
    """
        Modelo para la clase Fase
    """
    nombre = models.CharField(max_length=15)
    proyecto = models.ForeignKey('gestion_de_proyecto.Proyecto', on_delete=models.CASCADE)
    #items = models.ForeignKey('Item', on_delete=models.CASCADE)
    #lineaBase = models.ForeignKey('LineaBase', on_delete=models.CASCADE, verbose_name="Linea Base")
    faseCerrada = models.BooleanField(verbose_name="Fase Cerrada")
    puedeCerrarse = models.BooleanField(verbose_name="Puede Cerrarse")

    class Meta:
        permissions = [
            ('pp_crear_fase', 'Crear Fase dentro de Proyecto'),
            ('pp_f_eliminar_fase', 'Eliminar Fase de Proyecto'),
            ('pp_f_cerrar_fase', 'Cerrar Fase de Proyecto'),
        ]