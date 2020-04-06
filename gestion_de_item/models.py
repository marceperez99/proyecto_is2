from django.db import models

# Create your models here.
from gestion_de_tipo_de_item.models import TipoDeItem

class EstadoDeItem:
    """
    Clase que especifica todos los estados en los que se puede encontrar un tipo de item

    Estados de un item:
        CREADO = "Creado"
        APROBADO = "Aprobado"
        EN_LINEA_BASE = "En Linea Base"
        ELIMINADO = "Eliminado"
        A_APROBAR = "Listo para su aprobación"
        EN_REVISION = "En Revisión"
        A_MODIFICAR = "A modificar"
    """
    CREADO = "Creado"
    APROBADO = "Aprobado"
    EN_LINEA_BASE = "En Linea Base"
    ELIMINADO = "Eliminado"
    A_APROBAR = "Listo para su aprobación"
    EN_REVISION = "En Revisión"
    A_MODIFICAR = "A modificar"


class Item(models.Model):
    """
    Modelo que representa a un item de una fase.
    TODO: COMENTAR!!!
    """
    tipo_de_item = models.ForeignKey(TipoDeItem)
    estado = models.CharField(max_length=40)
    codigo = models.CharField(max_length = 40) #TODO: construir en el field tipo_de_item.prefijo + #order
    #version = models.ForeignKey(VersionItem,on_delete=CASCADE)

    def get_fase(self):
        fase = self.tipo_de_item.fase
        return fase

class VersionItem(models.Model):


