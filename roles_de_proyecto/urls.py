from django.urls import path
from .views import nuevo_rol_de_proyecto_view, editar_rol_de_proyecto_view, \
    listar_roles_de_proyecto_view, rol_de_proyecto_view, eliminar_rol_de_proyecto_view

urlpatterns = [
    path('', listar_roles_de_proyecto_view, name='listar_roles_de_proyecto'),
    path('nuevo/', nuevo_rol_de_proyecto_view, name='nuevo_rol_de_proyecto'),
    path('<int:id_rol>/editar', editar_rol_de_proyecto_view, name='editar_rol_de_proyecto'),
    path('<int:id_rol>/', rol_de_proyecto_view, name='rol_de_proyecto'),
    path('<int:id_rol>/eliminar', eliminar_rol_de_proyecto_view, name='eliminar_rol_de_proyecto'),
]