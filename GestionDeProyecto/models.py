from django.db import models
#from usuario import models

# Create your models here.

"""
Tranqui que esto se va a borrar despues
    #blank = True and null = True permite dejar en blanco
    #help_text ayuda en el formulario
    # verbose_name para renombrar en el panel el nombre
"""



class Proyecto(models.Model):
    nombre = models.CharField(max_length=15)
    descripcion = models.CharField(max_length=50)
    creador = models.ForeignKey('Usuario')
    fechaCreacion = models.DateField(verbose_name="Fecha de Creacion")
    estado = models.CharField(max_length=10, verbose_name="Estado del Proyecto")
    #participantes = models.ForeignKey('Participante') ??
    #participaComo ??
    fases = models.ForeignKey('Fase')