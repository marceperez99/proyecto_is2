from django.db import models

# Create your models here.

class Fase(models.Model):
    """
        Modelo para la clase Fase
    """
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey('gestion_de_proyecto.Proyecto',on_delete=models.CASCADE,null=True)
    descripcion = models.CharField(max_length=300)
    #items = models.ForeignKey('Item', on_delete=models.CASCADE)
    #lineaBase = models.ForeignKey('LineaBase', on_delete=models.CASCADE, verbose_name="Linea Base")
    fase_cerrada = models.BooleanField(verbose_name="Fase Cerrada")
    puede_cerrarse = models.BooleanField(verbose_name="Puede Cerrarse")

    def __str__(self):
        return self.nombre
    class Meta:
        permissions = [
            ('pp_crear_fase', 'Crear Fase dentro de Proyecto'),
            ('pp_f_eliminar_fase', 'Eliminar Fase de Proyecto'),
            ('pp_f_cerrar_fase', 'Cerrar Fase de Proyecto'),
        ]