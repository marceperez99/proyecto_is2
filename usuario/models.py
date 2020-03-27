from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
# Create your models here.


class Usuario(User):
    """
    Modelo proxy que extiende el modelo User de Django.

    """
    class Meta:
        proxy = True
