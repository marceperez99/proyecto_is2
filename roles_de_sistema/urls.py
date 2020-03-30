from django.urls import path
from .views import nuevo_rol_de_sistema_view, editar_rol_de_sistema_view, \
    listar_roles_de_sistema_view, rol_de_sistema_view, eliminar_rol_de_sistema_view

urlpatterns = [
    path('', listar_roles_de_sistema_view, name='listar_roles_de_sistema'),
    path('nuevo/', nuevo_rol_de_sistema_view, name='nuevo_rol_de_sistema'),
    path('<int:id_rol>/editar', editar_rol_de_sistema_view, name='editar_rol_de_sistema'),
    path('<int:id_rol>/', rol_de_sistema_view, name='rol_de_sistema'),
    path('<int:id_rol>/eliminar', eliminar_rol_de_sistema_view, name='eliminar_rol_de_sistema'),
]