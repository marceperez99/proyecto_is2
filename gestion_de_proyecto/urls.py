from django.urls import path
from . import views


urlpatterns = [
    path('nuevo/', views.nuevo_proyecto_view, name='nuevoProyecto'),
    #path('visualizarProyecto/', views.visualizar_proyecto_view, name='visualizarProyecto'),
    #path('', views.visualizar_proyectos_view, name='visualizarProyectos'),
    #path('editar/', views.editar_proyecto_view, name='editarProyecto'),

]
