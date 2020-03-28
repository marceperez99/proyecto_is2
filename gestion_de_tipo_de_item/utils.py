def get_dict_tipo_de_item(tipo):
    """
    Funcion que toma un tipo de item y retorna un diccionario con todos los datos del tipo de item
    :param tipo:
    :return:
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
