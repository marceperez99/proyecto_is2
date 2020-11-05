from django.urls import path

from . import views

urlpatterns = [
    path('', views.listar_solicitudes_view, name='solicitudes_de_cambio'),
    path('<int:solicitud_id>/', views.solicitud_view, name='solicitud_de_cambio'),
    path('<int:solicitud_id>/votar/', views.solicitud_votacion_view, name='votar_solicitud'),
    path('reporte/', views.generar_reporte, name="generar_reporte_de_solicitudes")

]
