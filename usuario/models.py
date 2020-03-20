from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Usuario(User):
    """
    Modelo proxy que extiende el modelo User de Django.

    """
    class Meta:
        proxy = True

