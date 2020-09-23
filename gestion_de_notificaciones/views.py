from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from gestion_de_notificaciones.models import Notificacion
from gestion_de_notificaciones.utils import send_mail


@login_required
def ver_notificaciones_view(request):
    unread_notifications = Notificacion.objects.filter(leido=False, usuario=request.user)
    read_notifications = Notificacion.objects.filter(leido=True, usuario=request.user)

    contexto = {
        'user': request.user,
        'read_notifications': read_notifications,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'gestion_de_notificaciones/listar_notificaciones.html', contexto)


@login_required
def visualizar_notificacion_view(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)
    contexto = {
        'user': request.user,
        'notificacion': notificacion
    }
    notificacion.read = True
    notificacion.save()
    return render(request, 'gestion_de_notificaciones/ver_notificacion.html', contexto)
