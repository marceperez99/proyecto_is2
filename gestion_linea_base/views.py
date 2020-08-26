from django.forms import formset_factory
from django.shortcuts import render
from django.utils import timezone

from gestion_de_item.models import Item
from gestion_de_proyecto.models import Comite, Proyecto
from gestion_de_solicitud.models import SolicitudDeCambio, EstadoSolicitud, Asignacion
from gestion_linea_base.forms import AsignacionForm, SolicitudForm
from gestion_linea_base.models import LineaBase


def solicitar_rompimiento_view(request, proyecto_id, fase_id, linea_base_id):
    linea_base = LineaBase.objects.get(id = linea_base_id)
    # TODO:Cambiar para tener solo los items de la linea base
    items = linea_base.items.all()
    asignacion_formset = formset_factory(AsignacionForm, extra=items.count(), can_delete=False)

    proyecto = Proyecto.objects.get(id=proyecto_id)

    if request.method == 'POST':
        solicitud_form = SolicitudForm(request.POST)
        formset = asignacion_formset(request.POST,form_kwargs={'proyecto_id': proyecto_id})
        print(request.POST)
        if solicitud_form.is_valid() and all(form.is_valid() for form in formset):

            solicitud = SolicitudDeCambio()
            solicitud.descripcion = solicitud_form.cleaned_data['razon_rompimiento']
            solicitud.solicitante = proyecto.get_participante(request.user)
            solicitud.estado = EstadoSolicitud.PENDIENTE
            solicitud.fecha = timezone.now()

            #Get a Linea Base
            solicitud.linea_base = linea_base
            #Consigue el numero de miembros
            comite = Comite.objects.get(proyecto=proyecto)
            solicitud.numero_de_miembros = comite.miembros.count()

            solicitud.save()
            count = 0
            for form in formset:
                print(form.cleaned_data)
                if form.cleaned_data and form.cleaned_data['modificar']:
                    asignacion = Asignacion()
                    asignacion.usuario = form.cleaned_data['usuario']
                    asignacion.solicitud = solicitud
                    asignacion.item = items[count]
                    asignacion.save()
                count = count + 1
            return render(request,'index')
    else:
        solicitud_form = SolicitudForm()

        formset = asignacion_formset(form_kwargs={'proyecto_id': proyecto_id})
        for form, item in zip(formset, items):
            form.item = item

    contexto = {'formset': formset, 'solicitud_form': solicitud_form, 'len': len(formset)}
    return render(request, 'gestion_linea_base/solicitar_rompimiento.html', context=contexto)
