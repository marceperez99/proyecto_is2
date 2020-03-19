from django.db import models
from django.contrib.auth.models import User
import reversion

# Create your models here.
reversion.register(User)
@reversion.register
class Usuario(User):
    """
    Modelo proxy que extiende el modelo User de Django.

    """
    class Meta:
        proxy = True

