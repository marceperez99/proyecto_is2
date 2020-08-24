from django.urls import path

from . import views

urlpatterns = [
    path('nuevo/', views.nueva_linea_base_view, name='nuevo_linea_base'),
]