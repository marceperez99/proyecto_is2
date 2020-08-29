from gestion_de_item.models import Item, VersionItem, AtributoItemNumerico, AtributoItemCadena, AtributoItemBooleano, \
    AtributoItemFecha
from gestion_de_proyecto.models import Participante


def item_factory(tipo, data):
    """
    Factory que retorna un objeto Item
    :param tipo: TipoDeItem
    :param data: dict() de la forma:
    {
        'estado': 'EstadoDeItem',
        'codigo': 'codigo',
        'encargado_de_modificar': 'username',
        'estado_anterior': 'Estado Anterior',
        'version':
        'versiones': {
            1:{

            }
        }
    }
    :return: Item
    """
    if isinstance(data, Item): return data
    item = Item(tipo_de_item=tipo, estado=data['estado'], codigo=data['codigo'])
    if 'encargado_de_modificar' in data.keys():
        item.encargado_de_modificar = Participante.objects.get(usuario__username=data['encargado_de_modificar'])
    if 'estado_anterior' in data.keys():
        item.estado_anterior = data['estado_anterior']

    for version, datos in data['versiones']:
        if data['version'] == version:
            item.version = version_factory(tipo, item, version, datos)
        else:
            version_factory(tipo, item, version, datos)

    item.save()
    return item


def version_factory(tipo_de_item, item, nro_version, data):
    """
    Factory que retorna objetos del tipo VersionItem
    :param item: Item
    :param nro_version: int
    :param data: dict() de la forma
    {
        'nombre': 'Nombre de item',
        'descripcion': 'Descripcion',
        'peso': int,
        'atributos_dinamicos': [
            {
                'campo': 'nombre_campo',
                'tipo': 'tipo de valor',
                'valor': 'valor'
            },{...},...
        ],
        'antecesores': ['codigo_item', 'codigo_item',...]
        'padres': ['codigo_item', 'codigo_item',...]
    }
    :return:
    """
    if isinstance(data, VersionItem): return data
    version = VersionItem.objects.create(item=item, nombre=data['nombre'], descripcion=data['descripcion'],
                                         version=nro_version, peso=data['peso'])

    for atributo in data['atributos_dinamicos']:
        if atributo['tipo'] == 'numerico':
            atributo_item_numerico_factory(tipo_de_item, version, atributo)

        elif atributo['tipo'] == 'cadena':
            atributo_item_cadena_factory(tipo_de_item, version, atributo)

        elif atributo['tipo'] == 'booleano':
            atributo_item_booleano_factory(tipo_de_item, version, atributo)

        elif atributo['tipo'] == 'fecha':
            atributo_item_fecha_factory(tipo_de_item, version, atributo)

    for antecesor in data['antecesores']:
        antecesor = Item.objects.filter(tipo_de_item__fase__proyecto=item.get_fase().proyecto).get(codigo=antecesor)
        version.antecesores.add(antecesor)

    for padre in data['padres']:
        padre = Item.objects.filter(tipo_de_item__fase=item.get_fase()).get(codigo=padre)
        version.antecesores.add(padre)

    return version


def atributo_item_numerico_factory(tipo_de_item, version, data):
    """
    Factory que produce objetos del tipo AtributoItemNumerico
    :param tipo_de_item: TipoDeItem
    :param version: VersionItem
    :param data: dict() de la forma:
    {
        'campo':'nombre del campo',
        'valor': numeric
    }
    :return: AtributoItemNumerico
    """
    field = tipo_de_item.atributonumerico_set.get(nombre=data['campo'])
    return AtributoItemNumerico.objects.create(version=version, plantilla=field, valor=data['valor'])


def atributo_item_cadena_factory(tipo_de_item, version, data):
    """
    Factory que produce objetos del tipo AtributoItemCadena
    :param tipo_de_item: TipoDeItem
    :param version: VersionItem
    :param data: dict() de la forma:
    {
        'campo':'nombre del campo',
        'valor': str
    }
    :return: AtributoItemCadena
    """
    field = tipo_de_item.atributocadena_set.get(nombre=data['campo'])
    return AtributoItemCadena.objects.create(version=version, plantilla=field, valor=data['valor'])


def atributo_item_booleano_factory(tipo_de_item, version, data):
    """
    Factory que produce objetos del tipo AtributoItemBooleano
    :param tipo_de_item: TipoDeItem
    :param version: VersionItem
    :param data: dict() de la forma:
    {
        'campo':'nombre del campo',
        'valor': Bool
    }
    :return: AtributoItemBooleano
    """
    field = tipo_de_item.atributobooleano_set.get(nombre=data['campo'])
    return AtributoItemBooleano.objects.create(version=version, plantilla=field, valor=data['valor'])


def atributo_item_fecha_factory(tipo_de_item, version, data):
    """
    Factory que produce objetos del tipo AtributoItemFecha
    :param tipo_de_item: TipoDeItem
    :param version: VersionItem
    :param data: dict() de la forma:
    {
        'campo':'nombre del campo',
        'valor': FechaHora
    }
    :return: AtributoItemFecha
    """
    field = tipo_de_item.atributofecha_set.get(nombre=data['campo'])
    return AtributoItemFecha.objects.create(version=version, plantilla=field, valor=data['valor'])
