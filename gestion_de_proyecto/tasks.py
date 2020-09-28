import os

from celery import shared_task

from gestion_de_notificaciones.utils import send_mail
from gestion_de_proyecto.models import Proyecto


@shared_task
def notificar_inicio_proyecto(proyecto_id,domain):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    participantes = proyecto.get_participantes()
    destinatarios = [participante.usuario.email for participante in participantes]
    contexto = {'proyecto': proyecto,'domain':domain}
    send_mail(destinatarios, titulo='Inicio de Proyecto',
              template='gestion_de_notificaciones/mails/inicio_proyecto.html', context=contexto)