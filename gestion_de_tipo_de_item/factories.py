from django.contrib.auth.models import User
from gestion_de_tipo_de_item.models import AtributoFecha, TipoDeItem, AtributoCadena, AtributoBinario, AtributoBooleano, \
    AtributoNumerico


def tipo_de_item_factory(fase, data):
    """
    Factory que crea tipos de items.
    :param fase: Fase de un proyecto
    :param data: dict() de la forma:
    {
        'nombre': 'nombre_tipo',
        'descripcion': 'descripcion',
        'prefijo': 'prefijo',
        'creador': 'username',
        'fecha_de_creacion': FechaHora,
        'atributos_dinamicos':[
            {
                'tipo':''
            }
        ]
    }
    :return:
    """
    if isinstance(data, TipoDeItem): return data
    creador = User.objects.get(username=data['creador'])
    tipo_de_item = TipoDeItem.objects.create(nombre=data['nombre'], descripcion=data['descripcion'], fase=fase,
                                             prefijo=data['prefijo'], creador=creador,
                                             fecha_creacion=data['fecha_de_creacion'])

    for atributo_dinamico in data['atributos_dinamicos']:
        if atributo_dinamico['tipo'] == 'archivo':
            atributo_dinamico_archivo_factory(tipo_de_item, atributo_dinamico)
        elif atributo_dinamico['tipo'] == 'cadena':
            atributo_dinamico_archivo_factory(tipo_de_item, atributo_dinamico)
        elif atributo_dinamico['tipo'] == 'booleano':
            atributo_dinamico_archivo_factory(tipo_de_item, atributo_dinamico)
        elif atributo_dinamico['tipo'] == 'numerico':
            atributo_dinamico_archivo_factory(tipo_de_item, atributo_dinamico)
        elif atributo_dinamico['tipo'] == 'fecha':
            atributo_dinamico_archivo_factory(tipo_de_item, atributo_dinamico)
        pass
    return tipo_de_item


def atributo_dinamico_archivo_factory(tipo_de_item, data):
    """
    Factory que retorna un AtributoBinario.
    :param tipo_de_item: TipoDeItem
    :param data: dict() de la forma:
    {
        'tipo': 'archivo',
        'nombre': 'nombre del campo',
        'requerido': Bool,
        'max_tamaño': int,
    }
    :return: AtributoBinario
    """
    return AtributoBinario.objects.create(tipo_de_item=tipo_de_item, nombre=data['nombre'], requerido=data['requerido'],
                                          max_tamaño=data['max_tamaño'])


def atributo_dinamico_cadena_factory(tipo_de_item, data):
    """
    Factory que retorna un AtributoCadena.
    :param tipo_de_item: TipoDeItem
    :param data: dict() de la forma:
    {
        'tipo': 'cadena',
        'nombre': 'nombre del campo',
        'requerido': Bool,
        'max_longitud': int,
    }
    :return: AtributoCadena
    """
    return AtributoCadena.objects.create(tipo_de_item=tipo_de_item, nombre=data['nombre'], requerido=data['requerido'],
                                         max_longitud=data['max_longitud'])


def atributo_dinamico_booleano_factory(tipo_de_item, data):
    """
        Factory que retorna un AtributoBooleano.
        :param tipo_de_item: TipoDeItem
        :param data: dict() de la forma:
        {
            'tipo': 'booleano',
            'nombre': 'nombre del campo',
        }
        :return: AtributoBooleano
        """
    return AtributoBooleano.objects.create(tipo_de_item=tipo_de_item, nombre=data['nombre'])


def atributo_dinamico_numerico_factory(tipo_de_item, data):
    """
    Factory que retorna un AtributoNumerico.
    :param tipo_de_item: TipoDeItem
    :param data: dict() de la forma:
    {
        'tipo': 'numerico',
        'nombre': 'nombre del campo',
        'requerido': Bool,
        'max_digitos': int,
        'max_decimales': int,
    }
    :return: AtributoNumerico
    """
    return AtributoNumerico.objects.create(tipo_de_item=tipo_de_item, nombre=data['nombre'],
                                           requerido=data['requerido'],
                                           max_digitos=data['max_digitos'], max_decimales=data['max_decimales'])


def atributo_dinamico_fecha_factory(tipo_de_item, data):
    """
    Factory que retorna un AtributoFecha.
    :param tipo_de_item: TipoDeItem
    :param data: dict() de la forma:
    {
        'tipo': 'fecha',
        'nombre': 'nombre del campo',
        'requerido': Bool
    }
    :return: AtributoFecha
    """
    return AtributoFecha.objects.create(tipo_de_item=tipo_de_item, nombre=data['nombre'], requerido=data['requerido'])
