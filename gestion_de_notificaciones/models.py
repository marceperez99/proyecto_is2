from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Notificacion(models.Model):
    """
    Modelo que guarda información de las notificaciones que se envian en el Sistema.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    mensaje = models.CharField(max_length=800)
    leido = models.BooleanField(default=False)
    fecha_de_creacion = models.DateTimeField(default=timezone.now)
