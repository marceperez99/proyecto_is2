import gestion_de_tipo_de_item.models as modelos
from gestion_de_item.forms import AtributoItemNumericoForm, AtributoItemBooleanoForm, AtributoItemFechaForm, \
    AtributoItemCadenaForm, AtributoItemArchivoForm


def get_atributos_forms(tipo_de_item, request):
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
    # TODO comentar y hacer PU
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
