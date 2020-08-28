from django.urls import path

from . import views

urlpatterns = [
    path('nuevo/', views.nueva_linea_base_view, name='nuevo_linea_base'),
    path('<int:linea_base_id>/', views.listar_linea_base_view, name='listar_linea_base'),
    path('<int:linea_base_id>/solicitar_rompimiento/', views.solicitar_rompimiento_view, name='solicitar_rompimiento'),
]
