from django.db import models


class Fase(models.Model):
    """
    Clase Fase del sistema. Esta clase sirve además como modelo para la creación de la Base de Datos.

    Clase Padre: models.Model

    Atributos:

        nombre: models.CharField

        proyecto: models.ForeignKey

        descripcion: models.CharField

        fase_anterior:  models.ForeignKey

        items = models.ForeignKey

        lineaBase = models.ForeignKey

        fase_cerrada = models.BooleanField

        puede_cerrarse = models.BooleanField

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

    class Meta:
        permissions = [
            ('g_pp_crear_fase', 'Crear Fase dentro de Proyecto'),
            ('g_pp_editar_fase', 'Editar Fase dentro de Proyecto'),
            ('g_pp_f_eliminar_fase', 'Eliminar Fase de Proyecto'),
            ('pp_f_ver_fase', 'Visualizar Fase dentro de Proyecto'),
            ('pp_f_cerrar_fase', 'Cerrar Fase de Proyecto'),
        ]

    def posicionar_fase(self):
        """
        Metodo que sirve para el posicionamiento de una nueva fase dento del proyecto, lo posiona correctamente
        al inicio o al medio de las fases que ya existen

        Agrs:
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