from django import db
from gdstorage.storage import GoogleDriveStorage

import gestion_de_tipo_de_item.models as modelos
from gestion_de_item.forms import AtributoItemNumericoForm, AtributoItemBooleanoForm, AtributoItemFechaForm, \
    AtributoItemCadenaForm, AtributoItemArchivoForm
from gestion_de_item.models import AtributoItemArchivo


def get_atributos_forms(tipo_de_item, request, instance=None):
    """
    Función utilitaria que construye una lista de forms para cada atributo del item asociado a su tipo de item.

    Argumentos:
        - tipo_de_item: TipoDeItem
        - request: HttpRequest

    Retorna
        atributo_forms: lista de forms adecuados para cada atributo.
   """

    atributo_forms = []
    counter = 0
    for atributo in tipo_de_item.get_atributos():
        counter = counter + 1
        if type(atributo) == modelos.AtributoCadena:
            atributo_forms.append(
                AtributoItemCadenaForm(request.POST or None, plantilla=atributo, counter=counter))
        elif type(atributo) == modelos.AtributoNumerico:
            atributo_forms.append(
                AtributoItemNumericoForm(request.POST or None, plantilla=atributo, counter=counter))
        elif type(atributo) == modelos.AtributoBinario:
            atributo_forms.append(
                AtributoItemArchivoForm(request.POST or None, request.FILES, plantilla=atributo, counter=counter))
        elif type(atributo) == modelos.AtributoFecha:
            atributo_forms.append(
                AtributoItemFechaForm(request.POST or None, plantilla=atributo, counter=counter))
        elif type(atributo) == modelos.AtributoBooleano:
            atributo_forms.append(
                AtributoItemBooleanoForm(request.POST or None, plantilla=atributo, counter=counter))
    return atributo_forms


def hay_ciclo(padre, hijo):
    """
    Funcion auxiliar del metodo "clean_padre", para determinar si al formar una relacion entre padre e hijo
    esta no va a formar un ciclo. El algoritmo utilizado es DFS iterativo.\n
    Argumentos: \n
        - padre: item de una fase\n
        - hijo: item de la misma fase\n
    Retorna: \n
        - True: si ya hay un camino directo o indirecto que conecta padre con hijo\n
        - False: si no hay un camnino que concecte padre con hijo\n
    """
    stack = []
    visitado = set()
    stack.append(padre)
    visitado.add(padre)
    while len(stack) != 0:
        item = stack.pop()
        for padre in item.padres.all():
            if padre not in visitado:
                stack.append(padre)
                visitado.add(padre)
    return hijo in visitado


def upload_and_save_file_item(gd_storage, atributo_id, file, proyecto, fase, item):
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
    db.close_old_connections()

    for i in range(0, len(atributo_id)):

        atributo = AtributoItemArchivo.objects.get(id=atributo_id[i])
        path = f'/PROY-{proyecto.nombre}-ID{proyecto.id}_/' \
               f'FASE-{fase.nombre}-ID{fase.id}_/ITEM-{item}_/ATRIB-{atributo.plantilla.nombre}_/' \
               f'VERS{atributo.version.version}_/FILENAME-{file[i].name}'

        gd_storage.save(path, file[i])
        atributo.valor = gd_storage.url(path)

        atributo.save()


def upload_and_save_file_item_2(atributo, file, proyecto, fase, item):
    gd_storage = GoogleDriveStorage()
    path = f'/PROY-{proyecto.nombre}-ID{proyecto.id}_/FASE-{fase.nombre}-ID{fase.id}_/ITEM-{item}_/ATRIB-{atributo.plantilla.nombre}_/VERS{atributo.version.version}_/FILENAME-{file.name}'
    print(path)
    gd_storage.save(path, file)
    return gd_storage.url(path)
