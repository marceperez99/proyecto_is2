from django.db import models
from gestion_de_item.models import Item

from gestion_de_item.models import EstadoDeItem
from gestion_linea_base.models import LineaBase


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
    fase_cerrada = models.BooleanField(verbose_name="Fase Cerrada")
    puede_cerrarse = models.BooleanField(verbose_name="Puede Cerrarse")

    def __str__(self):
        return self.nombre

    def es_primera_fase(self):
        """
        Metodo que retorna si la fase es la primera fase del proyecto.

        Retorna:
            - True si la fase es la primera fase del proyecto, False en caso contrario
        """
        return self.fase_anterior is None

    def es_ultima_fase(self):
        """
        Metodo de la clase Fase, que dice si esta fase es la ultima del proyecto.

        Retorna:
            -True: Si la fase es la ultima del proyecto
            -False: Si la fase no es la ultima del proyecto
        """
        list = self.proyecto.get_fases()
        if list[-1].id == self.id:
            return True
        return False

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


    def cerrar(self):
        """
        Metodo que se encarga de verificar si una fase dentro del proyecto puede ser cerrada,
        para ello todos los item deben estar en una linea base cerrada, todos ellos deben ser trazables a la siguiente
        fase directa o indirectamente y la fase anterior debe estar con estado cerrada.
        Las exceptiones serian la primera fase, que pasaria de alto la ragla de la fase anterior carrada, y la
        ultima fase, que pasaria de alto los item trazables a la siguiente fase.

        Lanza:
            -Exception, si la fase no se puede cerrar, esto es, si no cumple las condiciones citadas arriba.
            Se mostraran todos los requisitos previos necesarios para cerrar la fase.
        """

        mensaje_error = []
        if not self.es_primera_fase() and self.fase_anterior.fase_cerrada is False:
            mensaje_error.append(f'La fase anterior {self.fase_anterior.nombre} todavia esta sin cerrar')

        items = self.get_items()
        for item in items:
            if item.estado != EstadoDeItem.EN_LINEA_BASE:
                mensaje_error.append(f'El item {item.version.nombre} no esta en una Linea Base')

        if not self.es_ultima_fase():
            item_trazables = set()
            for item in items:
                if len(item.get_sucesores()) > 0:
                    item_trazables.add(item)

            item_relacionados = [i for i in items if
                                 i not in item_trazables and any(hijo in item_trazables for hijo in i.get_hijos())]

            while len(item_relacionados) > 0:
                for item in item_relacionados:
                    item_trazables.add(item)
                item_relacionados = [i for i in items if
                                     i not in item_trazables and any(hijo in item_trazables for hijo in i.get_hijos())]

            for item in items:
                if not (item in item_trazables):
                    mensaje_error.append(f'El item {item.version.nombre} no es trazable a la siguiente fase')

        if len(mensaje_error):
            raise Exception(mensaje_error)
        else:
            self.fase_cerrada = True
            self.save()


    def get_items(self, items_eliminados=False, en_revision=False):
        """
        Metodo que retorna los items asociados a una fase.

        Argumentos:
            items_eliminados: bandera para indicar si se retornarán todos los items de la fase, incluyendo
            aquellos que ya fueron eliminados.

        Retorna:
            list(): lista de todos los items de la fase del proyecto.
        """
        tipos = self.tipodeitem_set.all()
        items = []
        for tipo in tipos:
            if en_revision:
                items.extend(list(tipo.item_set.all().filter(estado=EstadoDeItem.EN_REVISION)))
            elif items_eliminados:
                # Se incluyen todos los items del tipo
                items.extend(list(tipo.item_set.all()))
            else:
                # Se excluyen los items eliminados
                items.extend(list(tipo.item_set.all().exclude(estado=EstadoDeItem.ELIMINADO)))

        return items

    def get_item_estado(self, *estado):
        """
        Metodo que devuelve todos los item de una fase que tengan los estados que se pasa como parametro\n
        Argumentos:\n
            estado: lista, estados de los items que se quieren\n
         Retorna:\n
            Todos los item con los estados pasado como paremetro dentro de la fase
        """
        tipos = self.tipodeitem_set.all()
        items = []
        for tipo in tipos:
            items.extend(list(tipo.item_set.filter(estado__in=estado)))

        items = [item.id for item in items]
        return Item.objects.filter(id__in=items)

    def get_lineas_base(self):
        return LineaBase.objects.filter(fase=self)


    def get_proyecto(self):
        return self.proyecto
