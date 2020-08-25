from django.urls import path

from . import views

urlpattern = [
    path('rompimiento/', views.solicitar_rompimiento_view, name='solicitar_rompimiento'),
]
