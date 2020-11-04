from django.urls import path

from . import views

urlpatterns = [
    path('usuario/', views.usuarios_view, name='usuarios'),
    path('usuario/reporte', views.usuarios_reporte_view, name='usuarios_reporte'),
    path('usuario/<int:usuario_id>/', views.usuario_view, name='perfil_de_usuario'),
    path('usuario/<int:usuario_id>/asignar_rs/', views.usuario_asignar_rol_view, name='asignar_rol_de_sistema'),
    path('usuario/<int:usuario_id>/desasignar_rs/', views.desasignar_rol_de_sistema_view,
         name='desasignar_rol_de_sistema'),
    path('usuario/mi_perfil/',views.mi_perfil_view,name='mi_perfil'),
    path('panel_de_control/', views.panel_de_administracion_view, name='panel_de_control'),
    path('panel_de_control/config_cloud', views.configurar_cloud_view, name='config_cloud')
]

