from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from gestion_de_fase.forms import FaseForm
from gestion_de_fase.models import Fase
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
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = FaseForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            nuevaFase = form.save(commit=False)
            nuevaFase.proyecto = proyecto
            nuevaFase.fase_cerrada = False
            nuevaFase.puede_cerrarse = False
            nuevaFase.save()
            nuevaFase.posicionar_fase()
            # Todo falta pone la url correcta
            return redirect('index')
    else:
        form = FaseForm(proyecto=proyecto)
    return render(request, 'gestion_de_fase/nueva_fase.html', {'formulario': form})


def editar_fase_view(request, proyecto_id, fase_id):
    """
    Vista que muestra al usuario los datos actuales de la fase que se pueden modificar, si el usuario
    desea cambiar, los cambia.
    Si el metodo Http con el que se realizo la peticion fue GET se muestra los datos que tiene la fase con la
    posibilidad de editarlos.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos cambiados y se guardan en la BD

    Args:\n
        request: HttpRequest.
        fase_id: int identificador unico de la fase que se quiere ver. \n
    Retorna:\n
        HttpResponse
    """
    fase = get_object_or_404(Fase, id=fase_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    form = FaseForm(request.POST or None, instance=fase, proyecto=proyecto)
    if request.method == 'POST':
        if form.is_valid():
            fase = form.save(commit=False)
            fase.save()
            fase.posicionar_fase()
            # Todo falta pone la url correcta
            return redirect('index')
    return render(request, 'gestion_de_fase/editar_fase.html', {'formulario': form})


def eliminar_fase_view(request, proyecto_id, fase_id):
    """
    Muestra una vista al usuario para que confirme la eliminacion de una fase.
    Si el metodo Http con el que se realizo la peticion fue GET se le pide al usuario que confirme la elimincion de una fase.
    Si el metodo Http con el que se realizo la peticion fue POST se procede a eliminar la fase.

    Args:\n
        request: HttpRequest.
        proyecto_id: int identificador unico del Proyecto que se quiere ver. \n
    Retorna:\n
        HttpResponse
    """
    fase = get_object_or_404(Fase, id=fase_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        if proyecto.fase_set.filter(fase_anterior=fase).exists():
            fase_derecha = proyecto.fase_set.get(fase_anterior=fase)
            fase_izquierda = fase.fase_anterior
            fase_derecha.fase_anterior = fase_izquierda
            fase_derecha.save()
        fase.delete()
        # Todo falta pone la url correcta
        return redirect('index')
    contexto = {'fase': fase, 'proyecto': proyecto}
    return render(request, 'gestion_de_fase/eliminar_fase.html', contexto)