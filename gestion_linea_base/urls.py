from django.urls import path

from . import views

urlpatterns = [
    path('solicitar_rompimiento/', views.solicitar_rompimiento_view, name='solicitar_rompimiento'),
    path('', views.listar_linea_base_view, name='listar_linea_base'),
    path('nuevo/', views.nueva_linea_base_view, name='nuevo_linea_base'),
]