from django.contrib.auth.decorators import login_required
from .forms import LineaBaseForm
from django.shortcuts import render, get_object_or_404, redirect
from gestion_de_fase.models import Fase
from .models import LineaBase, EstadoLineaBase
from gestion_de_proyecto.models import Proyecto
from django.urls import reverse


@login_required
#@permission_required('roles_de_sistema.pa_crear_proyecto', login_url='sin_permiso')
def nueva_linea_base_view(request, proyecto_id, fase_id):

    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase_id)
    if request.method == 'POST':
        form = LineaBaseForm(request.POST, proyecto=proyecto, fase=fase)
        if form.is_valid():
            lineabase = form.save(commit=False)
            lineabase.fase = get_object_or_404(Fase, id=fase_id)
            lineabase.estado = EstadoLineaBase.CERRADO
            lineabase.save()
            return redirect("visualizar_fase", proyecto_id=proyecto_id, fase_id=fase_id)
    else:
        form = LineaBaseForm(proyecto=proyecto, fase=fase)
    contexto = {'formulario': form,
                'breadcrumb': {'pagina_actual': 'Nueva Linea Base',
                               'links': [{'nombre': 'Panel de Administracion',
                                          'url': reverse('visualizar_fase', args=(proyecto_id, fase_id))}]}
                }

    return render(request, 'gestion_linea_base/nuevo_linea_base.html', contexto)

# Create your views here.
