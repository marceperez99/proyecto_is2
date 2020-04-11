from django.db import models

# Create your models here.
from gestion_de_tipo_de_item.models import *


class EstadoDeItem:
    """
    Clase que especifica todos los estados en los que se puede encontrar un tipo de item

    Estados de un item:
        - CREADO = "Creado"
        - APROBADO = "Aprobado"
        - EN_LINEA_BASE = "En Linea Base"
        - ELIMINADO = "Eliminado"
        - A_APROBAR = "Listo para su aprobación"
        - EN_REVISION = "En Revisión"
        - A_MODIFICAR = "A modificar"
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

    - tipo_de_item: TipoDeItem, el tipo de este ite,
    - estado: EstadoItem, estado en que se encuentra el item
    - version: VersionItem, versión actual de este item.

    """
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)
    estado = models.CharField(max_length=40)
    codigo = models.CharField(max_length=40)  # TODO: construir en el field: tipo_de_item.prefijo + #order
    version = models.ForeignKey('gestion_de_item.VersionItem', null=True, related_name='item_version',
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.version.nombre

    def get_fase(self):
        return self.tipo_de_item.fase

    def get_peso(self):
        return self.version.peso

    def get_antecesores(self):
        return self.version.antecesores

    def get_padres(self):
        return self.version.padres

    def get_numero_version(self):
        return self.version.version

    def get_atributos_dinamicos(self):
        """
        Metodo que retorna la lista de atributos dinamicos del Item.

        Retorna:
            list(): lista de objetos AtributoItemNumerico, AtributoItemFecha,
        """
        atributos = list(self.version.atributoitemnumerico_set.all())
        atributos += list(self.version.atributoitemfecha_set.all())
        atributos += list(self.version.atributoitemcadena_set.all())
        atributos += list(self.version.atributoitembooleano_set.all())
        atributos += list(self.version.atributoitemarchivo_set.all())
        return atributos

    def get_versiones(self):
        """
        Metodo que retorna la lista de versiones de un determinado Item.

        Retorna
            list(): lista de objetos Version, con los datos de la version del item
        """
        # TODO verificar que esto retorne correctamente las versiones
        return self.version_item.all().order_by('-version')

    def eliminar(self):
        """
        Meétodo del model Item que permite cambiar el estado de un item a ELIMINADO. En caso de exito retorna True.

        Retorna: True or False (Eliminado o no)
        """
        if self.estado == EstadoDeItem.CREADO:
            self.estado = EstadoDeItem.ELIMINADO
            self.save()
            return True
        return False


class VersionItem(models.Model):
    """
    Modelo que representa una versión de un ítem junto a sus atributos versionables.

    - nombre: string
    - descripcion: string
    - peso: int
    - antecesores: lista[] items
    - padres: lista[] items
    - version: int

    """

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='version_item')
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=400)
    version = models.IntegerField()  # TODO: construir en el field: item.version_item_set.all.count() + 1
    peso = models.IntegerField()
    antecesores = models.ManyToManyField(Item, related_name='antecesores')
    padres = models.ManyToManyField(Item, related_name='padres')


class AtributoItemArchivo(models.Model):
    """
    Modelo que representa un atributo dinámico de tipo archivo de un item. Sus especificaciones estan dadas por la plantilla del attributo de tipo archivo del tipo de item correspondiente.

    """
    version = models.ForeignKey(VersionItem, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(AtributoBinario, on_delete=models.CASCADE)
    valor = models.CharField(max_length=500, null=True)
    # TODO: Marcos, podes cambiar esto si ves necesario. Puede llamarse valor tambien para ser estandar.


class AtributoItemBooleano(models.Model):
    """
        Modelo que representa un atributo dinámico de tipo booleano de un item. Sus especificaciones estan dadas por la plantilla del attributo de tipo booleano del tipo de item correspondiente.

    """

    version = models.ForeignKey(VersionItem, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(AtributoBooleano, on_delete=models.CASCADE)
    valor = models.BooleanField(null=True)


class AtributoItemFecha(models.Model):
    """
    Modelo que representa un atributo dinámico de tipo fecha de un item. Sus especificaciones estan dadas por la plantilla del attributo de tipo fecha del tipo de item correspondiente.

    """
    version = models.ForeignKey(VersionItem, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(AtributoFecha, on_delete=models.CASCADE)
    valor = models.DateTimeField(null=True)


class AtributoItemNumerico(models.Model):
    """
        Modelo que representa un atributo dinámico de tipo númerico de un item. Sus especificaciones estan dadas por la plantilla del attributo de tipo númerico del tipo de item correspondiente.

    """
    version = models.ForeignKey(VersionItem, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(AtributoNumerico, on_delete=models.CASCADE)
    valor = models.DecimalField(decimal_places=20, max_digits=40, null=True)


class AtributoItemCadena(models.Model):
    """
        Modelo que representa un atributo dinámico de tipo cadena de un item. Sus especificaciones estan dadas por la plantilla del attributo de tipo cadena del tipo de item correspondiente.

    """
    version = models.ForeignKey(VersionItem, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(AtributoCadena, on_delete=models.CASCADE)
    valor = models.CharField(max_length=500, null=True)
