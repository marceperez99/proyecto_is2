
import os
from celery import shared_task
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Comite
from gestion_linea_base.models import LineaBase
from gestion_de_notificaciones.utils import send_mail
from gestion_de_solicitud.models import SolicitudDeCambio


@shared_task
def notificar_solicitud_lb_cancelada(solicitud_id):
    """
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
    Función asincrona que construye un mensaje para ser enviado por correo utilizando la función utilitaria send_mail.

    Argumentos:
        - solicitud_id: int, id de la solicitud de cambio que se quiere hacer.
    """
    solicitud = SolicitudDeCambio.objects.get(id=solicitud_id)
    destinatario = solicitud.solicitante
    contexto = {'solicitud': solicitud}
    send_mail([destinatario.usuario.email], titulo='Solicitud de rompimiento de LB Aceptada',
              template='gestion_de_notificaciones/mails/solicitud_lb_aceptada.html', context=contexto)

@shared_task
def notificar_solicitud_de_rompimiento(proyecto_id, fase_id, linea_base_id, solicitud_id, domain):
    """
       Función asincrona que construye un mensaje para ser enviado por correo utilizando la función utilitaria send_mail.

       Argumentos:
           - proyecto_id: int, id del proyecto iniciado.
           - fase_id: int, id de la fase donde se encientra el item.
           - linea_base_id: int, id de la linea base que se desea romper
           - domain: str, dominio del sistema.
       """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    fase = Fase.objects.get(id=fase_id)
    linea_base = LineaBase.objects.get(id=linea_base_id)
    solicitud = SolicitudDeCambio.objects.get(id=solicitud_id)
    comite = Comite.objects.get(proyecto=proyecto)
    destinatarios = [participante.usuario.email for participante in comite.miembros.all()]
    contexto = {'proyecto': proyecto, 'fase': fase, 'linea_base': linea_base, 'solicitud': solicitud, 'domain': domain}
    send_mail(destinatarios, titulo='Solicitud de Rompimiento',
              template='gestion_de_notificaciones/mails/solicitud_de_rompimiento.html', context=contexto)
   