from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .tasks import mail_for_new_user
from .models import Usuario


@receiver(post_save, sender=User)
def save_user(sender, instance, created, **kwargs):
    """
    Funcion utilitaria que se encarga de llamar a la funcion que envia un mail a los Administradores del sistema, cada
    vez que un usuario es creado.

    Argumentos:
        - sender: Clase del Usuario.
        - instance: Instancia del Usuario.
        - created: Bandera que identifica si la instancia del usuario fue creada o editada.

    Retorna:
        - Void
    """
    if created:
        print('User created')
        mail_for_new_user.delay(instance.id)