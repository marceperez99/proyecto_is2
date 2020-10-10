from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .tasks import mail_for_new_user
from .models import Usuario


@receiver(post_save, sender=User)
def save_user(sender, instance, created, **kwargs):
    if created:
        print('User created')
        mail_for_new_user.delay(instance.id)