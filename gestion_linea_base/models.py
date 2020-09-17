from django.db import models
from gestion_de_item.models import Item


class EstadoLineaBase:
    # TODO: Marcos, poner en planilla.
    """
        Clase que especifica todos los estados en los que se puede encontrar una Linea de Base

        Estados de un item:
            - CERRADA = "Cerrada"
            - COMPROMETIDA = "Comprometida"
            - ROTA = "Rota"
        """
    CERRADA = "Cerrada"
    COMPROMETIDA = "Comprometida"
    ROTA = "Rota"


class LineaBase(models.Model):
    # TODO: Marcos, poner en planilla.
    """
        Modelo que representa a una Linea de Base en una Fase

        -nombre: Nombre del Ítem
        -estado = EstadoLineaBase, estado en el que se encuentra el Ítem
        -items = Lista de items que están incluidas en la Linea de Base
        -fecha_creacion = Fecha de creación de la Linea de Base
        -fase = Fase a la que pertenece la Linea de Base
    """
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
