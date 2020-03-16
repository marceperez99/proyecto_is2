from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Usuario(User):
    class meta:
        proxy = True

    #metodo de prueba
    def introduccion(self):
        return "Hola, mi nombre es {}".format(self.first_name)
