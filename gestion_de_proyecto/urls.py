from django.urls import path
from . import views


urlpatterns = [
    path('nuevo/', views.nuevo_proyecto_view, name='nuevo_proyecto'),
    path('<int:proyecto_id>/', views.visualizar_proyecto_view, name='visualizar_proyecto'),
    path('<int:proyecto_id>/editar/', views.editar_proyecto_view, name='editar_proyecto'),
    path('<int:proyecto_id>/cancelar/', views.cancelar_proyecto_view, name='cancelar_proyecto'),
    path('<int:proyecto_id>/participante/nuevo/', views.nuevo_participante_view, name='nuevo_participante'),
    path('<int:proyecto_id>/permisos_insuficientes', views.pp_insuficientes, name='pp_insuficientes'),
]
