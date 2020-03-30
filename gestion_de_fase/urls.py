from django.urls import path
from . import views


urlpatterns = [
    path('', views.listar_fase_view, name='listar_fases'),
    path('nueva/', views.nueva_fase_view, name='nueva_fase'),
    path('<int:fase_id>/', views.visualizar_fase_view, name='visualizar_fase'),
    path('<int:fase_id>/editar/', views.editar_fase_view, name='editar_fase'),
    path('<int:fase_id>/eliminar/', views.eliminar_fase_view, name='eliminar_fase'),

]