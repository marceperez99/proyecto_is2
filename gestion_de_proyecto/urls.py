from django.urls import path
from . import views


urlpatterns = [
    path('nuevo/', views.nuevo_proyecto_view, name='nuevo_proyecto'),
    path('<int:proyecto_id>/', views.visualizar_proyecto_view, name='visualizar_proyecto'),
    #path('', views.visualizar_proyectos_view, name='visualizarProyectos'),
    #path('editar/', views.editar_proyecto_view, name='editarProyecto'),
    path('<int:proyecto_id>/participante/<int:participante_id>/', views.participante_view,
         name='participante'),
    path('<int:proyecto_id>/participante/', views.participantes_view, name='participantes'),
    path('<int:proyecto_id>/participante/<int:participante_id>/eliminar', views.eliminar_participante_view,
         name='eliminar_participante'),
]
