from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission, User
from django.test import Client
from django.urls import reverse

from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante
from .models import RolDeProyecto
from datetime import datetime
@pytest.fixture
def usuario():
    user = User(username='user_test', email='test@admin.com')
    user.set_password('password123')
    user.save()
    return user

@pytest.fixture
def rol_de_proyecto():
    rol = RolDeProyecto(nombre='Desarrollador',descripcion='Descripcion del rol')
    rol.save()
    rol.asignar_permisos([p for p in Permission.objects.filter(codename__startswith='pp_')])
    return rol

@pytest.fixture
def proyecto(usuario,rol_de_proyecto):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba', fechaCreacion=datetime.today(),
                        creador=usuario)

    fase = Fase(nombre='Analisis', proyecto=proyecto, faseCerrada=False, puedeCerrarse=False)
    fase.save()
    fase = Fase(nombre='Desarrollo', proyecto=proyecto, faseCerrada=False, puedeCerrarse=False)
    fase.save()
    fase = Fase(nombre='Pruebas', proyecto=proyecto, faseCerrada=False, puedeCerrarse=False)
    fase.save()

    participante = Participante(proyecto=proyecto, usuario=usuario)
    participante.save()

    proyecto.save()
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
