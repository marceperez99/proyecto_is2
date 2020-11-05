from gestion_linea_base.models import LineaBase


def create_nombre_LB(proyecto, fase):
    """
    Función utilitaria que construye el nombre para la Línea de Base de tal forma que estos no se repitan,
    el patron de nonbre será "LB_<nro_fase>_<nro_lb>"

    Argumentos:
        - proyecto: Proyectos
        - fase: Fase

    Retorna
        El nombre único para la linea de Base a crear.
   """
    nro_fase = proyecto.get_fases().index(fase) + 1
    nro_lb = LineaBase.objects.filter(fase=fase).__len__() + 1
    return "LB_" + str(nro_fase) + "_" + str(nro_lb)
