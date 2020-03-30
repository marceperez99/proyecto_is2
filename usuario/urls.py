from django.urls import path
from . import views
urlpatterns = [
    path('usuario/', views.usuarios_view, name='usuarios'),
    path('usuario/<int:usuario_id>/', views.usuario_view, name='perfil_de_usuario'),
    path('usuario/<int:usuario_id>/asignar_rs/', views.usuario_asignar_rol_view, name='asignar_rol_de_sistema'),
    path('panel_de_control/', views.panel_de_administracion_view, name='panel_de_control')
]
