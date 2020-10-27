import os

from celery import shared_task


from gestion_de_notificaciones.utils import send_mail
from gestion_de_solicitud.models import SolicitudDeCambio


@shared_task
def notificar_solicitud_lb_cancelada(solicitud_id):
    """
    #TODO Luis, cargar en planilla
    Función asincrona que construye un mensaje para ser enviado por correo utilizando la función utilitaria send_mail.

    Argumentos:
        - solicitud_id: int, id de la solicitud de cambio que se quiere hacer.
    """
    solicitud = SolicitudDeCambio.objects.get(id=solicitud_id)
    destinatario = solicitud.solicitante
    contexto = {'solicitud': solicitud}
    send_mail([destinatario.usuario.email], titulo='Solicitud de rompimiento de LB Cancalada',
              template='gestion_de_notificaciones/mails/solicitud_lb_cancelada.html', context=contexto)

@shared_task
def notificar_solicitud_lb_aceptada(solicitud_id):
    """
    #TODO Luis, cargar en planilla
    Función asincrona que construye un mensaje para ser enviado por correo utilizando la función utilitaria send_mail.

    Argumentos:
        - solicitud_id: int, id de la solicitud de cambio que se quiere hacer.
    """
    solicitud = SolicitudDeCambio.objects.get(id=solicitud_id)
    destinatario = solicitud.solicitante
    contexto = {'solicitud': solicitud}
    send_mail([destinatario.usuario.email], titulo='Solicitud de rompimiento de LB Aceptada',
              template='gestion_de_notificaciones/mails/solicitud_lb_aceptada.html', context=contexto)