from gestion_de_tipo_de_item.models import *
from gestion_de_item.forms import *


def get_atributos_forms(tipo_de_item, request):
    """

    :param tipo_de_item:
    :param request:
    :return:
    """
    atributo_forms = []
    counter = 0
    for atributo in tipo_de_item.get_atributos():
        counter = counter + 1
        if type(atributo) == AtributoCadena:
            atributo_forms.append(
                AtributoItemCadenaForm(request.POST or None, plantilla=atributo, counter=counter))
        elif type(atributo) == AtributoNumerico:
            atributo_forms.append(
                AtributoItemNumericoForm(request.POST or None, plantilla=atributo, counter=counter))
        elif type(atributo) == AtributoBinario:
            atributo_forms.append(
                AtributoItemArchivoForm(request.POST or None,request.FILES, plantilla=atributo, counter=counter))
        elif type(atributo) == AtributoFecha:
            atributo_forms.append(
                AtributoItemFechaForm(request.POST or None, plantilla=atributo, counter=counter))
        elif type(atributo) == AtributoBooleano:
            atributo_forms.append(
                AtributoItemBooleanoForm(request.POST or None, plantilla=atributo, counter=counter))
    return atributo_forms
