from django.urls import path
from . import views


urlpatterns = [
    path('nueva/', views.nueva_fase_view, name='nueva_fase'),
    path('<int:fase_id>/editar/', views.editar_fase_view, name='editar_fase'),
]