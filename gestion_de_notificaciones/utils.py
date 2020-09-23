from django.contrib.auth.models import User
from django.template.loader import render_to_string
import django.core.mail as mail

from gestion_de_notificaciones.models import Notificacion


def send_mail(destinatarios: list, titulo: str, template: str, context=None):
    """
    Funcion encargada de crear notificaciones y enviar los correos correspondientes.

    Los correos se envian desde el correo electronico especificado en los settings.
    Se pueden enviar correos a varios usuarios a la vez

    Argumentos:
     - destinatarios: list(), lista de correos electronicos a los que se enviara el correo
     - titulo: str(), Titulo del mail
     - template: str(), template que se va a evaluar y sera el cuerpo del mail
     - context: dict(), contexto para pasar informacion al template

    Ejemplo de uso:
        >>> send_mail(['marce-1999@fpuna.edu.py'],'Asignacion de Rol de Sistema',
        'gestion_de_notificaciones/mails/nuevo_rol_de_sistema.html',context={'rol':'Administrador'})
    """
    mensaje = render_to_string(template, context=context)

    for email in destinatarios:
        user = User.objects.get(email=email)
        Notificacion.objects.create(usuario=user, titulo=titulo, mensaje=mensaje)

    mail.send_mail(titulo, "mensaje", None, destinatarios)
