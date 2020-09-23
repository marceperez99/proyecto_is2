from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    mensaje = models.CharField(max_length=800)
    leido = models.BooleanField(default=False)
    fecha_de_creacion = models.DateTimeField(default=timezone.now)
