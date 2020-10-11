import os

from celery import shared_task
from django.contrib.auth.models import User, Group
from gestion_de_notificaciones.utils import send_mail
from .models import Usuario


@shared_task
def mail_for_new_user(id_user):
    """
    Funcion utilitaria que se encarga de enviar un mail a los Administradores del sistema,
    informando que un usuario a sido creado y necesita un Rol de Sistema.

    Argumentos:
        - id_user: Id del usuario creado

    Retorna:
        - Void
    """
    user = User.objects.get(id=id_user)
    admins = User.objects.filter(groups__name='Administrador')
    mail_admins = [a.email.__str__() for a in admins]
    [print(m) for m in mail_admins]
    send_mail(mail_admins, 'Acceso de Nuevo Usuario', 'gestion_de_notificaciones/mails/nuevo_usuario.html',
              context={'mail': user.email})


@shared_task
def mail_for_new_rol(id_usuario):
    """
        Funcion utilitaria que se encarga de enviar un mail al Usuario recibido como parametro,
        informandole que se le ha asignado un nuevo Rol de Sistema.

        Argumentos:
            - id_usuario: Id del usuario

        Retorna:
            - Void
        """
    usuario = Usuario.objects.get(id=id_usuario)
    send_mail([usuario.email], 'Rol Asignado', 'gestion_de_notificaciones/mails/rol_asignado.html',
              context={'nombre': usuario.get_full_name().__str__(),
                       'rol': usuario.get_rol_de_sistema().nombre.__str__()})
