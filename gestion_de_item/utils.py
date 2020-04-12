from gestion_de_tipo_de_item.models import TipoDeItem


def hay_ciclo(padre, hijo):
    #TODO comentar y hacer PU
    stack = []
    visitado = set()
    stack.append(padre)
    visitado.add(padre)
    while len(stack) != 0:
        item = stack.pop()
        for padre in item.padres.all():
            if padre not in visitado:
                stack.append(padre)
                visitado.add(item)
    return hijo in visitado
