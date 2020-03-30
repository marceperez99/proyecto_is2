from django.utils import timezone

from gestion_de_tipo_de_item.forms import AtributoCadenaForm, AtributoNumericoForm, AtributoBooleanoForm, \
    AtributoFechaForm, AtributoArchivoForm


def guardar_atributos(atributos_forms, tipo_de_item):
    for form in atributos_forms:
        atributo = form.save(commit=False)
        atributo.tipo_de_item = tipo_de_item
        atributo.save()


def guardar_tipo_de_item(tipo_de_item, fase, usuario):
    """
    Función utilitaria que dada un tipo de item, una fase y un user guarda el tipo de item relacionandolo con la fase
    y al usuario como su creador.

    Argumentos:
        tipo_de_item: TipoDeItem\n
        fase: Fase\n
        usuario: Usuario\n

    Retorna:
        None
    """
    tipo_de_item.fase = fase
    tipo_de_item.creador = usuario
    tipo_de_item.fecha_creacion = timezone.now()
    tipo_de_item.save()


def atributo_form_handler(atributos_dinamicos):
    """
    Función utilitaria que dada una lista de atibutos representados como un diccionario contruye un form adecuado
    para cada atributo.

    Argumentos:
        atributos_dinamicos: lista[] de diccionarios Atributo

    Retorna
        atributos_forms: lista[] de forms para cada atributo.
    """
    atributos_forms = []
    for atributo in atributos_dinamicos:
        if 'tipo' not in atributo.keys():
            continue
        if atributo['tipo'] == 'cadena':
            atributos_forms.append(AtributoCadenaForm(atributo))
        elif atributo['tipo'] == 'numerico':
            atributos_forms.append(AtributoNumericoForm(atributo))
        elif atributo['tipo'] == 'booleano':
            atributos_forms.append(AtributoBooleanoForm(atributo))
        elif atributo['tipo'] == 'fecha':
            atributos_forms.append(AtributoFechaForm(atributo))
        elif atributo['tipo'] == 'archivo':
            atributos_forms.append(AtributoArchivoForm(atributo))
    return atributos_forms


def construir_atributos(request):
    """
    TODO: Marcelo comentame esto.
    """
    # Lista de atributos dinamicos
    atributos_dinamicos = [dict() for x in range(int(request.POST['cantidad_atributos']))]
    # Se filtran todos los atributos dinamicos
    atributos_de_items = {key: request.POST[key] for key in request.POST if key.startswith("atr_")}
    # se crea una lista con todos los atributos dinamicos
    for atributo in atributos_de_items.keys():
        partes = atributo.split("_", maxsplit=2)
        atributos_dinamicos[int(partes[1]) - 1][partes[2]] = atributos_de_items[atributo]
    return atributos_dinamicos


def recolectar_atributos(tipo_de_item):
    """
    Función utilitaria que dado un TipoDeItem construye un lista con todos los atributos relacionados a este tipo de item.

    Argumentos:
        tipo_de_item: TipoDeItem

    Retorna:
        atributos_dinamicos: lista[] de diccionarios para cada atributo


    >>> print(recolectar_atributos(tipo1))
    [
        {'tipo': 'cadena', 'nombre': 'Descripción', 'max_longitud': '400', 'requerido': 'on'},
        {'tipo': 'numerico', 'nombre': 'Costo del caso de uso', 'max_digitos': '2', 'max_decimales': '2'},
        {'tipo': 'archivo', 'nombre': 'Diagrama del caso de uso', 'max_tamaño': '5'},
        {'tipo': 'fecha', 'nombre': 'Fecha de Cierre', 'requerido': 'on'}
    ]

    """
    atributos_dinamicos = []
    atributos_texto = tipo_de_item.atributocadena_set.all()
    for atributo in atributos_texto:
        diccionario = {}
        diccionario.update(tipo='cadena')
        diccionario.update(nombre=atributo.nombre)
        diccionario.update(max_longitud=str(atributo.max_longitud))
        if atributo.requerido:
            diccionario.update(requerido='on')
        atributos_dinamicos.append(diccionario)

    atributos_numerico = tipo_de_item.atributonumerico_set.all()
    for atributo in atributos_numerico:
        diccionario = {}
        diccionario.update(tipo='numerico')
        diccionario.update(nombre=atributo.nombre)
        diccionario.update(max_digitos=str(atributo.max_digitos))
        diccionario.update(max_decimales=str(atributo.max_decimales))
        if atributo.requerido:
            diccionario.update(requerido='on')
        atributos_dinamicos.append(diccionario)

    atributos_archivo = tipo_de_item.atributobinario_set.all()
    for atributo in atributos_archivo:
        diccionario = {}
        diccionario.update(tipo='archivo')
        diccionario.update(nombre=atributo.nombre)
        diccionario.update(max_tamaño=str(atributo.max_tamaño))
        if atributo.requerido:
            diccionario.update(requerido='on')
        atributos_dinamicos.append(diccionario)

    atributos_fecha = tipo_de_item.atributofecha_set.all()
    for atributo in atributos_fecha:
        diccionario = {}
        diccionario.update(tipo='fecha')
        diccionario.update(nombre=atributo.nombre)
        if atributo.requerido:
            diccionario.update(requerido='on')
        atributos_dinamicos.append(diccionario)

    atributos_booleano = tipo_de_item.atributobooleano_set.all()
    for atributo in atributos_booleano:
        diccionario = {}
        diccionario.update(tipo='booleano')
        diccionario.update(nombre=atributo.nombre)
        if atributo.requerido:
            diccionario.update(requerido='on')
        atributos_dinamicos.append(diccionario)
    return atributos_dinamicos


def get_dict_tipo_de_item(tipo):
    """
    Funcion que toma un tipo de item y retorna un diccionario con todos los datos del tipo de item
    TODO: marcelo
    """
    atributos = {'nombre': tipo.nombre, 'descripcion': tipo.descripcion, 'atributos_dinamicos': []}

    for atributo in tipo.atributocadena_set.all():
        atributos['atributos_dinamicos'].append({
            'nombre': atributo.nombre,
            'tipo': 'Texto',
            'requerido': 'Si' if atributo.requerido else 'No',
            'max_longitud': atributo.max_longitud
        })
    for atributo in tipo.atributobooleano_set.all():
        atributos['atributos_dinamicos'].append({
            'nombre': atributo.nombre,
            'tipo': 'Booleano',
            'requerido': 'Si' if atributo.requerido else 'No',
        })
    for atributo in tipo.atributofecha_set.all():
        atributos['atributos_dinamicos'].append({
            'nombre': atributo.nombre,
            'tipo': 'Fecha',
            'requerido': 'Si' if atributo.requerido else 'No',
        })
    for atributo in tipo.atributonumerico_set.all():
        atributos['atributos_dinamicos'].append({
            'nombre': atributo.nombre,
            'tipo': 'Numerico',
            'requerido': 'Si' if atributo.requerido else 'No',
            'max_digitos': atributo.max_digitos,
            'max_decimales': atributo.max_decimales,
        })
    for atributo in tipo.atributobinario_set.all():
        atributos['atributos_dinamicos'].append({
            'nombre': atributo.nombre,
            'tipo': 'Archivo',
            'requerido': 'Si' if atributo.requerido else 'No',
            'max_tamaño': atributo.max_tamaño
        })
    return atributos
