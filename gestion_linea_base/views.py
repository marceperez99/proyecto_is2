from django.forms import formset_factory
from django.shortcuts import render

from gestion_de_item.models import Item
from gestion_linea_base.forms import AsignacionForm, SolicitudForm


def solicitar_rompimiento_view(request, proyecto_id, fase_id, linea_base_id):
    # TODO:Cambiar para tener solo los items de la linea base
    items = list(Item.objects.all())

    solicitud_form = SolicitudForm()
    asignacion_formset = formset_factory(AsignacionForm, extra=len(items), can_delete=False)
    formset = asignacion_formset()
    for form, item in zip(formset, items):
        form.item = item
    contexto = {'formset': formset, 'solicitud_form': solicitud_form,'len' : len(formset)}

    return render(request, 'gestion_linea_base/solicitar_rompimiento.html', context=contexto)
