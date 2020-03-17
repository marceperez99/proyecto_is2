from django.urls import path
from .views import nuevo_rol_de_proyecto_view
urlpatterns = [
   path('nuevo/',nuevo_rol_de_proyecto_view,name='nuevo_rol_de_proyecto')
]