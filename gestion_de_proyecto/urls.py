from django.urls import path
from . import views


urlpatterns = [
    path('nuevo/', views.nuevo_proyecto_view, name='nuevo_proyecto'),
    path('<int:proyecto_id>/', views.visualizar_proyecto_view, name='visualizar_proyecto'),
    #path('', views.visualizar_proyectos_view, name='visualizarProyectos'),
    #path('editar/', views.editar_proyecto_view, name='editarProyecto'),

]
