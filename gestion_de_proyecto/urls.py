from django.urls import path
from . import views

urlpatterns = [
    path('nuevo/', views.nuevo_proyecto_view, name='nuevoProyecto'),
    # path('visualizarProyecto/', views.visualizar_proyecto_view, name='visualizarProyecto'),
    # path('', views.visualizar_proyectos_view, name='visualizarProyectos'),
    # path('editar/', views.editar_proyecto_view, name='editarProyecto'),
    path('<int:proyecto_id>/participante/<int:participante_id>/', views.participante_view,
         name='participante'),
    path('<int:proyecto_id>/participante/', views.participantes_view, name='participantes'),
    path('<int:proyecto_id>/participante/<int:participante_id>/eliminar', views.eliminar_participante_view,
         name='eliminar_participante'),
]
