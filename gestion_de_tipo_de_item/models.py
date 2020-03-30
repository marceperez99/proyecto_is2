from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from gestion_de_fase.models import Fase
from django.utils.timezone import timezone


# Create your models here.
class TipoDeItem(models.Model):
    """
    Modelo que representa una instancia de un tipo de item.

    Atributos:
        nombre: string\n
        descripcion: string\n
        prefijo: string\n
        creador: User\n
        fase: Fase\n
        fecha_creacion: date\n

    """
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=400)
    prefijo = models.CharField(max_length=20)
    creador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField()

    def __str__(self):
        return self.nombre

    def get_atributos(self):
        """
        Método que consigue la lista completa de atributos dinámico

        Retorna:
            atributos: lista[] atributos dinámicos asociados a este tipo de item.
        """
        atributos = []
        atributos += list(self.atributocadena_set.all())
        atributos += list(self.atributonumerico_set.all())
        atributos += list(self.atributobooleano_set.all())
        atributos += list(self.atributobinario_set.all())
        atributos += list(self.atributofecha_set.all())
        return atributos


class AtributoBinario(models.Model):
    """
    Modelo que representa la definición de un atributo dinámico del tipo archivo asociado a un tipo de item

    Atributos:
        nombre: string\n
        requerido: boolean\n
        max_tamaño: int\n
        tipo_de_item: TipoDeItem\n
    """

    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    max_tamaño = models.IntegerField(verbose_name="Tamaño Máximo (MB)",
        validators=[MinValueValidator(1, "El tamaño maximo para el archivo debe ser mayor o igual a 1MB")])

    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.requerido


class AtributoCadena(models.Model):
    """
       Modelo que representa la definición de un atributo dinámico del tipo Cadena asociado a un tipo de item

       Atributos:
            nombre: string\n
            requerido: boolean\n
            max_longitud: int\n
            tipo_de_item: TipoDeItem\n
       """
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    max_longitud = models.IntegerField(verbose_name='Longitud Maxima',
                                       validators=[MinValueValidator(0,"La longitud maxima de la cadena debe ser un numero mayor o igual a 0"),
                                                   MaxValueValidator(500, "La longlitud maxima de la cadena es 500")])
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.valor


class AtributoBooleano(models.Model):
    """
       Modelo que representa la definición de un atributo dinámico del tipo Booleano asociado a un tipo de item

       Atributos:
           nombre: string\n
           requerido: boolean\n
           tipo_de_item: TipoDeItem\n
       """
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.requerido


class AtributoNumerico(models.Model):
    """
       Modelo que representa la definición de un atributo dinámico del tipo Númerico asociado a un tipo de item

       Atributos:
           nombre: string\n
           requerido: boolean\n
           max_digitos: int\n
           max_decimales: int\n
           tipo_de_item: TipoDeItem\n
       """
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    max_digitos = models.IntegerField(verbose_name='Maxima cantidad de digitos',
                                      validators=[MinValueValidator(0,
                                                                    "La máxima cantidad de digitos debe ser un numero mayor o igual a 0"),
                                                  MaxValueValidator(20,
                                                                    "El máximo numero de digitos permitidos es 20")])
    max_decimales = models.IntegerField(verbose_name='Maxima cantidad de posiciones decimales',
                                        validators=[MinValueValidator(0,
                                                                      "La máxima cantidad de digitos decimales debe ser un numero mayor o igual a 0"),
                                                    MaxValueValidator(20,
                                                                      "El máximo numero de digitos decimales permitidos es 20")])
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.requerido


class AtributoFecha(models.Model):
    """
       Modelo que representa la definición de un atributo dinámico del tipo Fecha asociado a un tipo de item

       Atributos:
           nombre: string\n
           requerido: boolean\n
           tipo_de_item: TipoDeItem\n
       """
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.requerido
