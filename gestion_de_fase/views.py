from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from gestion_de_fase.forms import NuevaFaseForm
from gestion_de_proyecto.models import Proyecto

# Create your views here.


def nueva_fase_view(request, proyecto_id):
    """
    Vista que se usa para la creacion y posicionamiento de una fase dentro de un proyecto
    Si el metodo Http con el que se realizo la peticion fue GET se muestra un formulario para completar.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan en la BD

    Args:

     request: HttpRequest

     proyecto_id: int identificador unico de un Proyecto

    Retorna:

     HttpResponse
    """
    proyecto=get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = NuevaFaseForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            nuevaFase = form.save(commit=False)
            nuevaFase.proyecto = proyecto
            nuevaFase.fase_cerrada = False
            nuevaFase.puede_cerrarse = False
            nuevaFase.save()
            nuevaFase.posicionar_fase()
            return redirect('index')
    else:
        form = NuevaFaseForm(proyecto=proyecto)
    return render(request, 'gestion_de_fase/nueva_fase.html', {'formulario': form})