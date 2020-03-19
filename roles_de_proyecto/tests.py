from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission, User
from django.test import Client
from django.urls import reverse

from .models import RolDeProyecto

@pytest.mark.django_db
def test_vista_crear_rol_usuario_loggeado():
    """
    Test encargado de comprobar que no ocurra nigun error al cargar la pagina con un usuario que ha iniciado sesion
    """
    user = User(username='user_test')
    user.set_password('12345')
    user.save()
    client = Client()
    client.login(username='user_test',password='12345')

    response = client.get(reverse('nuevo_rol_de_proyecto'))

    assert response.status_code == HTTPStatus.OK, 'Hubo un error al cargar la pagina, '

@pytest.mark.django_db
def test_RolDeProyecto_lista_de_permisos():
    """
    Prueba unitaria encargada de probar metodo get_permisos para asegurarse que al tratar de obtener los permisos de un rol
    creado retorne una lista con esos
    """
    permisos = list(Permission.objects.all())
    rol = RolDeProyecto(nombre='rol1',descripcion="descripcion")
    rol.save()
    rol.permisos.set(permisos)

    permisos_obtenidos = rol.get_permisos()

    assert permisos_obtenidos == permisos, "Los permisos asignados al rol no fueron guardados correctamente"

@pytest.mark.django_db
def test_RolDeProyecto_lista_de_permisos_vacia():
    """
    Prueba unitaria encargada de probar metodo get_permisos para asegurarse que al tratar de obtener los permisos de un rol creado
    sin permisos retorne una lista vacia
    """
    rol = RolDeProyecto(nombre='rol1',descripcion="descripcion")
    rol.save()

    permisos_obtenidos = rol.get_permisos()

    assert permisos_obtenidos == [], "Los permisos asignados al rol no fueron guardados correctamente, "
