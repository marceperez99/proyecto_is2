from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from gestion_de_fase.models import Fase


# Create your models here.
class TipoDeItem(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=400)
    creador = models.ForeignKey(User, on_delete=models.SET_NULL)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)


class AtributoBinario(models.Model):
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    max_tamaño = models.IntegerField(
        validators=[MinValueValidator(1, "El tamaño maximo para el archivo debe ser mayor o igual a 1")])
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.requerido


class AtributoCadena(models.Model):
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    max_longitud = models.IntegerField(
        validators=[MinValueValidator(0, "La longitud maxima de la cadena debe ser un numero mayor o igual a 0"),
                    MaxValueValidator(500, "La longlitud maxima de la cadena es 500")])
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.valor


class AtributoBooleano(models.Model):
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.valor


class AtributoNumerico(models.Model):
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    max_digitos = models.IntegerField(
        validators=[MinValueValidator(0, "La maxima cantidad de digitos debe ser un numero mayor o igual a 0"),
                    MaxValueValidator(20, "El maximo numero de digitos permitidos es 20")])
    max_decimales = models.IntegerField(
        validators=[MinValueValidator(0, "La maxima cantidad de digitos decimales debe ser un numero mayor o igual a 0"),
                    MaxValueValidator(20, "El maximo numero de digitos decimales permitidos es 20")])
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.requerido


class AtributoFecha(models.Model):
    nombre = models.CharField(max_length=100)
    requerido = models.BooleanField()
    tipo_de_item = models.ForeignKey(TipoDeItem, on_delete=models.CASCADE)

    def es_requerido(self):
        return self.requerido