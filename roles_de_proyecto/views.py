from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import NewRolDeProyectoForm
# Create your views here.

@login_required
#TODO: falta agregar que esta funcion requiere el PS de crear nuevo rol de proyecto
def nuevo_rol_de_proyecto_view(request):
    """
    Vista que permite a un usuario crear un nuevo Rol de Proyecto dentro del sistema.

    Si al vista recibe un HttpRequest enviado con el metodo GET mostrará al usuario la pantalla de creacion de nuevo Rol.

    En cambio, si recibe el HttpRequest con el metodo POST tomará los datos recibidos y creará un nuevo Rol de Proyecto dentro del Sistema.

    Esta vista requiere que el usuario haya iniciado sesion y que cuente con el Permiso de Sistema correspondiente
    para crear un nuevo Rol de Proyecto.

    Args:

    request: HttpRequest, peticion Http recibida por el servidor de un usuario.

    Retorna:

    HttpResponse
    """
    contexto={'user':request.user}
    if(request.method == 'POST'):
        form = NewRolDeProyectoForm(request.POST)
        if(form.is_valid()):
            form.save()

        return redirect('nuevo_rol_de_proyecto')
    else:
        contexto['form'] = NewRolDeProyectoForm()

        return render(request,'roles_de_proyecto/nuevo_rol.html',context=contexto)