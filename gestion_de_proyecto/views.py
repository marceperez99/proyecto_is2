from django.shortcuts import render
import datetime

# Create your views here.


def nuevo_proyecto_view(request):
    contexto = {'fecha': datetime.datetime.now(), 'user': "USUARIO_AQUI"}
    render(request, 'nuevo_proyecto.html', context=contexto)
