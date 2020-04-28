from celery import shared_task

from gestion_de_item.models import AtributoItemArchivo


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
        atributo.archivo_temporal = None
        atributo.save()
