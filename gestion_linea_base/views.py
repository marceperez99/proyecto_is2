from django.contrib.auth.decorators import permission_required, login_required
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.utils import timezone

from gestion_de_item.models import Item
from gestion_de_proyecto.models import Comite, Proyecto
from gestion_de_solicitud.models import SolicitudDeCambio, EstadoSolicitud, Asignacion
from gestion_linea_base.forms import AsignacionForm, SolicitudForm
from gestion_linea_base.models import LineaBase
from roles_de_proyecto.decorators import pp_requerido_en_fase


@login_required
@permission_required('roles_de_sistema.pu_acceder_sistema', login_url='sin_permiso')
@pp_requerido_en_fase("pp_f_solicitar_ruptura_de_linea_base")
def solicitar_rompimiento_view(request, proyecto_id, fase_id, linea_base_id):
    """
    Vista que permite la creación de nuevas solicitudes de rompimiento de lineas bases cerradas.

    Argumentos:
        - request: HttpRequest
        - proyecto_id: int, id del proyecto
        - fase_id: int, id de la fase
        - linea_base_id: int, id de la linea base
    Retorna:
        - HttpResponse
    """
    # TODO: Verificar que la linea base este cerrada con un fixture

    linea_base = LineaBase.objects.get(id=linea_base_id)
    items = linea_base.items.all()
    asignacion_formset = formset_factory(AsignacionForm, extra=items.count(), can_delete=False)

    proyecto = Proyecto.objects.get(id=proyecto_id)

    if request.method == 'POST':
        solicitud_form = SolicitudForm(request.POST)
        formset = asignacion_formset(request.POST, form_kwargs={'proyecto_id': proyecto_id, 'fase_id': fase_id})
        print(request.POST)
        if solicitud_form.is_valid() and all(form.is_valid() for form in formset):

            solicitud = SolicitudDeCambio()
            solicitud.descripcion = solicitud_form.cleaned_data['razon_rompimiento']
            solicitud.solicitante = proyecto.get_participante(request.user)
            solicitud.estado = EstadoSolicitud.PENDIENTE
            solicitud.fecha = timezone.now()

            # Get a Linea Base
            solicitud.linea_base = linea_base
            # Consigue el numero de miembros
            comite = Comite.objects.get(proyecto=proyecto)
            solicitud.numero_de_miembros = comite.miembros.count()

            solicitud.save()
            count = 0
            for form in formset:
                if form.cleaned_data and form.cleaned_data['modificar']:
                    asignacion = Asignacion()
                    asignacion.usuario = form.cleaned_data['usuario']
                    asignacion.solicitud = solicitud
                    asignacion.item = items[count]
                    asignacion.motivo = form.cleaned_data['motivo']
                    asignacion.save()
                count = count + 1
            # TODO: debe retornar a la vista de la linea base.
            return redirect('index')
    else:
        solicitud_form = SolicitudForm()

        formset = asignacion_formset(form_kwargs={'proyecto_id': proyecto_id, 'fase_id': fase_id})
        for form, item in zip(formset, items):
            form.item = item
    contexto = {'formset': formset, 'solicitud_form': solicitud_form, 'len': len(formset)}
    return render(request, 'gestion_linea_base/solicitar_rompimiento.html', context=contexto)
