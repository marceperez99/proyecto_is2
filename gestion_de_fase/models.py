from django.db import models


class Fase(models.Model):
    """
    Clase Fase del sistema. Esta clase sirve además como modelo para la creación de la Base de Datos.

    Clase Padre:
        models.Model

    Atributos:
        nombre: models.CharField \n
        proyecto: models.ForeignKey \n
        descripcion: models.CharField \n
        fase_anterior:  models.ForeignKey \n
        items = models.ForeignKey \n
        lineaBase = models.ForeignKey \n
        fase_cerrada = models.BooleanField \n
        puede_cerrarse = models.BooleanField \n
        permisos: models.ManyToManyField, representa la relacion de un rol con los permisos que incluye.
    """
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

    def posicionar_fase(self):
        """
        Metodo que sirve para el posicionamiento de una nueva fase dento del proyecto, lo posiona correctamente
        al inicio o al medio de las fases que ya existen.

        Argumentos:
            fase: fase recien creada
        """
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

    def get_items(self):
        tipos = self.tipodeitem_set.all()
        items = []
        for tipo in tipos:
            items.extend(list(tipo.item_set.all()))

        return items
