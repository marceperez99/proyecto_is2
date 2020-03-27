from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from gestion_de_proyecto.forms import ProyectoForm
from .models import Proyecto

# Create your views here.

def nuevo_proyecto_view(request):
    """
    Vista que se usa para la creacion de un proyecto
    Si el metodo Http con el que se realizo la peticion fue GET se muestra un formulario para completar.
    Si el metodo Http con el que se realizo la peticion fue POST se toman los datos recibidos y se guardan en la BD

    Args:

        request: HttpRequest

    Retorna:

        HttpResponse
    """
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.fechaDeCreacion = timezone.now()
            proyecto.estado = "En Configuracion"
            proyecto.save()
            return redirect('index')
    else:
        form = ProyectoForm()
    return render(request, 'gestion_de_proyecto/nuevo_proyecto.html', {'formulario': form})



def visualizar_proyecto_view(request, proyecto_id):
    """
    Vista que muestra al usuario toda la informacion de un proyecto.

    Args:

        request: HttpRequest
        proyecto_id: int identificador unico del Proyecto que se quiere ver

    Retorna:

        HttpResponse
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    contexto={'user': request.user, 'proyecto': proyecto}
    return render(request,'gestion_de_proyecto/visualizar_proyecto.html',contexto)