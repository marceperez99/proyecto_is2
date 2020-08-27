from django.db import models
from gestion_de_item.models import Item


class EstadoLineaBase:
    CERRADO = "Cerrada"
    COMPROMETIDA = "Comprometida"
    ROTA = "Rota"

class LineaBase(models.Model):
    # TODO: Marcos, documentar.
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=40)
    items = models.ManyToManyField(Item)
    fase= models.ForeignKey('gestion_de_fase.Fase', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nombre


    def romper(self):
        # TODO comentar e incluir en planilla y probar
        self.estado = EstadoLineaBase.ROTA
        self.save()
    def create_nombre(self, proyecto, fase):
        nro_fase = proyecto.get_fases().index(fase) + 1
        nro_lb = LineaBase.objects.filter(fase__proyecto=proyecto).__len__()+1
        return "LB_"+str(nro_fase)+"_"+str(nro_lb)
