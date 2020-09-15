from django.db import models
from gestion_de_item.models import Item


class EstadoLineaBase:
    CERRADA = "Cerrada"
    COMPROMETIDA = "Comprometida"
    ROTA = "Rota"


class LineaBase(models.Model):
    # TODO: Marcos, documentar.
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=40)
    items = models.ManyToManyField(Item)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fase = models.ForeignKey('gestion_de_fase.Fase', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nombre

    def romper(self):
        # TODO comentar e incluir en planilla y probar
        self.estado = EstadoLineaBase.ROTA
        self.save()

    def create_nombre(self, proyecto, fase):
        nro_fase = proyecto.get_fases().index(fase) + 1
        # TODO: Marcos, no se numeran bien las lineas base, por ejemplo, si ya existen LB_1_1  y LB_1_2, si quiero crear
        #  la primera LB en la segunda fase esto hace que se llame LB_2_3 en vez de LB_2_1
        nro_lb = LineaBase.objects.filter(fase__proyecto=proyecto).__len__() + 1
        return "LB_" + str(nro_fase) + "_" + str(nro_lb)

    def get_proyecto(self):
        # TODO comentar e incluir en planilla y probar
        return self.fase.get_proyecto()

    def comprometer(self):
        """
        TODO: cargar en la planilla
        :return:
        """
        assert self.estado == EstadoLineaBase.CERRADA
        self.estado = EstadoLineaBase.COMPROMETIDA
        self.save()

    def esta_cerrada(self):
        """
        TODO: cargar en la planilla
        :return:
        """
        return self.estado == EstadoLineaBase.CERRADA
