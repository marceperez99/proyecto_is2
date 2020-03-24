from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from gestion_de_fase.forms import NuevaFaseForm
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto

# Create your views here.


def nueva_fase_view(request, proyecto_id):
    proyecto=get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = NuevaFaseForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            nuevaFase = form.save(commit=False)
            nuevaFase.proyecto = proyecto
            nuevaFase.fase_cerrada = False
            nuevaFase.puede_cerrarse = False
            nuevaFase.save()

            fase_posterior = Fase.objects.get()


            return redirect('index')
    else:
        form = NuevaFaseForm(proyecto=proyecto)
    return render(request, 'gestion_de_fase/nueva_fase.html', {'formulario': form})