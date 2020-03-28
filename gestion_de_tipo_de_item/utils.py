from django.utils import timezone

from gestion_de_tipo_de_item.forms import AtributoCadenaForm, AtributoNumericoForm, AtributoBooleanoForm, \
    AtributoFechaForm, AtributoArchivoForm


def guardar_atributos(atributos_forms, tipo_de_item):
    for form in atributos_forms:
        atributo = form.save(commit=False)
        atributo.tipo_de_item = tipo_de_item
        atributo.save()


def guardar_tipo_de_item(tipo_de_item, fase, user):
    tipo_de_item.fase = fase
    tipo_de_item.creador = user
    tipo_de_item.fecha_creacion = timezone.now()
    tipo_de_item.save()


def atributo_form_handler(atributos_dinamicos):
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
    # Lista de atributos dinamicos
    atributos_dinamicos = [dict() for x in range(int(request.POST['cantidad_atributos']))]
    # Se filtran todos los atributos dinamicos
    atributos_de_items = {key: request.POST[key] for key in request.POST if key.startswith("atr_")}
    # se crea una lista con todos los atributos dinamicos
    for atributo in atributos_de_items.keys():
        partes = atributo.split("_", maxsplit=2)
        atributos_dinamicos[int(partes[1]) - 1][partes[2]] = atributos_de_items[atributo]
    return atributos_dinamicos
