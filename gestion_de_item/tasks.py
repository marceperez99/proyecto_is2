import os

from celery import shared_task

from gestion_de_item.models import AtributoItemArchivo
from gestion_de_notificaciones.utils import send_mail
from gestion_de_proyecto.models import Proyecto
from gestion_de_fase.models import Fase
from gestion_de_item.models import Item

@shared_task
def tarea():
    print("Hola soy una tarea asincrona")


@shared_task
def upload_and_save_file_item(id_atributos):
    """
    Funcion utilitaria que se encarga de subir al repositorio de GoogleDrive la lista de archivos de los atributos
    dinamicos de un item, una vez subido cada arcivo se guardará el enlace de descarga en cada atributo.

    Argumentos:
        - gd_storage: Objeto que se comunuca con GDrive\n
        - atributo_id: Lista de ids de atributos e tipo aarchivo\n
        - file: Lista de archivos asociados a cada atributo\n
        - proyecto: Proyecto en el que se ecuentra el item\n
        - fase: Fase del Proyecto en el que se encuentra el item\n
        - item: Item que posee los atributos\n

    Retorna:
        - Void
    """
    for atributoid in id_atributos:
        atributo = AtributoItemArchivo.objects.get(id=atributoid)

        atributo.valor.save(atributo.archivo_temporal.name, atributo.archivo_temporal)
        # Se elimina el archivo del servidor
        if atributo.archivo_temporal:
            if os.path.isfile(atributo.archivo_temporal.path):
                os.remove(atributo.archivo_temporal.path)

        atributo.archivo_temporal = None
        atributo.save()


@shared_task
def notificar_solicitud_aprobacion_item(proyecto_id, fase_id, item_id, domain):
    """
    #TODO Luis, cargar en planilla
    Función asincrona que construye un mensaje para ser enviado por correo utilizando la función utilitaria send_mail.

    Argumentos:
        - proyecto_id: int, id del proyecto iniciado.
        - fase_id: int, id de la fase donde se encientra el item.
        - item_id: int, id del item solicitado para su aprevacion
        - domain: str, dominio del sistema.
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    fase = Fase.objects.get(id=fase_id)
    item = Item.objects.get(id=item_id)
    participantes = proyecto.get_participantes()
    destinatarios = [participante.usuario.email for participante in participantes if participante.tiene_pp_en_fase(fase,'pp_f_aprobar_item')]
    contexto = {'proyecto': proyecto,'fase': fase, 'item': item, 'domain':domain}
    send_mail(destinatarios, titulo='Solicitud de Aprobacion',
              template='gestion_de_notificaciones/mails/solicitud_aprobacion.html', context=contexto)