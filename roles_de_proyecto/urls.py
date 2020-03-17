from django.urls import path
from .views import nuevo_rol_de_proyecto_view, editar_rol_de_proyecto_view, \
   listar_roles_de_proyecto_view

urlpatterns = [
   path('', listar_roles_de_proyecto_view, name='listar_roles'),
   path('nuevo/', nuevo_rol_de_proyecto_view, name='nuevo_rol_de_proyecto'),
   path('<int:id_rol>/editar', editar_rol_de_proyecto_view, name='editar_rol_de_proyecto'),
]