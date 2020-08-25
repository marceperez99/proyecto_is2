from django.urls import path

from . import views

urlpatterns = [
    path('solicitar_rompimiento/', views.solicitar_rompimiento_view, name='solicitar_rompimiento'),
]
