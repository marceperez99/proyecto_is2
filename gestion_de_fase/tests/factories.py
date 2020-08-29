from gestion_de_fase.models import Fase


def fase_factory(proyecto, fase_anterior, data):
    if isinstance(data, Fase): return data
    return Fase.objects.create(nombre=data['nombre'], descripcion=data['descripcion'], proyecto=proyecto,
                               fase_anterior=fase_anterior, fase_cerrada=data['fase_cerrada'],
                               puede_cerrarse=data['puede_cerrarse'])
