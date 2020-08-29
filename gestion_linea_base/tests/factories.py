from gestion_linea_base.models import LineaBase


def linea_base_factory(fase, data):
    """
    Factory que retorna un objeto del tipo LineaBase
    :param fase: Fase
    :param data: dict() de la forma:
    {
        'nombre': 'Nombre',
        'estado': 'EstadoLB',
        'items': ['codigo_item', 'codigo_item',...]
    }
    :return:
    """
    lb = LineaBase.objects.create(nombre=data['nombre'],estado=data['estado'], fase=fase)
    for item in data['items']:
        lb.items.add(item)

    return lb
