from django.db import models

# Create your models here.

class Fase(models.Model):
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey('gestion_de_proyecto.Proyecto', on_delete=models.CASCADE,null=True)
    descripcion = models.CharField(max_length=300)
    fase_anterior = models.ForeignKey('gestion_de_fase.Fase', on_delete=models.SET_NULL, null=True)
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

    def posicionar_fase(self):
        if self.fase_anterior is None:
            if Fase.objects.all().filter(fase_anterior__isnull=True).exclude(id=self.id).filter(proyecto=self.proyecto).exists():
                fase_segunda = Fase.objects.all().filter(fase_anterior__isnull=True).exclude(id=self.id).filter(proyecto=self.proyecto)[0]
                fase_segunda.fase_anterior = self
                fase_segunda.save()
        else:
            if Fase.objects.all().filter(fase_anterior=self.fase_anterior).exclude(id=self.id).filter(proyecto=self.proyecto).exists():
                fase_derecha = Fase.objects.all().filter(fase_anterior=self.fase_anterior).exclude(id=self.id).filter(proyecto=self.proyecto)[0]
                fase_derecha.fase_anterior = self
                fase_derecha.save()