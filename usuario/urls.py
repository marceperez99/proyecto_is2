from django.urls import path
from . import views
urlpatterns = [
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/<int:usuario_id>', views.usuario_view, name='usuario'),
    path('usuarios/<int:usuario_id>/asignar_rs', views.usuario_asignar_rol_view, name='usuario'),
]
