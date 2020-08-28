from django.urls import path

from . import views

urlpattern = [
    path('rompimiento/', views.solicitar_rompimiento_view, name='solicitar_rompimiento'),
    path('solicitud/', views.listar_solicitudes_view, name='solicitudes_de_cambio'),
    path('solicitud/<int:solicitud_id>/', views.solicitud_view, name='solicitud_de_cambio'),
    path('solicitud/<int:solicitud_id>/votar/', views.solicitud_votacion_view, name='votar_solicitud'),

]
