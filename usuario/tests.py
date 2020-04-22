from http import HTTPStatus

import pytest
from django.contrib.auth.models import User, Permission, Group
from django.test import Client
from django.urls import reverse
from pytest import fixture

from roles_de_sistema.models import RolDeSistema


@pytest.fixture
def rs_admin():
    rol = RolDeSistema(nombre='Admin', descripcion='descripcion de prueba')
    rol.save()
    for pp in Permission.objects.filter(content_type__app_label='roles_de_sistema', codename__startswith='p'):
        rol.permisos.add(pp)
    rol.save()
    return rol


@pytest.fixture
def usuario(rs_admin):
    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    user.groups.add(Group.objects.get(name=rs_admin.nombre))
    return user

# Pruebas Unitarias


class TestModeloUsuario:
    # TODO: Marcos test asignar_rol_a_usuario
    # TODO: Marcos test desasignar_rol_a_usuario
    # TODO: Marcos test get_rol_de_sistema
    # TODO: Marcos test get_permisos_list
    # TODO: Marcos test get_proyectos
    # TODO: Marcos test get_proyectos_activos
    pass


@pytest.mark.django_db
class TestVistasUsuarios:
    @fixture
    def admin_loggeado(self, usuario, rs_admin):

        client = Client()
        client.login(username=usuario.username, password='12345')
        return client

    def test_ver_usuario_existente(self, admin_loggeado, usuario):
        """
        Prueba el acceso a la información de un usuario existente dentro del sistema. \n
        Accede a /usuarios/id con id igual a la clave primaria del usuario creado.

        Resultado esperado:
            Una respuesta HTTP con código 200

        Mensaje Error:
            No se puede acceder a '/usuarios/id' para un usuario existente.
        """
        response = admin_loggeado.get(reverse('perfil_de_usuario', args=(usuario.id,)))
        assert response.status_code == HTTPStatus.OK, 'No se puede acceder a \'/usuarios/id\' para un usuario existente.'

    def test_ver_usuario_no_existente(self, rs_admin, admin_loggeado, usuario):
        """
        Prueba el acceso a la información de un usuario no existente dentro del sistema. \n
        Accede a /usuarios/id con id distinto al de la clave primaria del usuario creado.

        Resultado esperado:
            Una respuesta HTTP con código 404

        Mensaje Error:
            El sistema muestra información de un usuario no existente.
        """
        response = admin_loggeado.get(reverse('perfil_de_usuario', args=(usuario.id + 1,)))
        assert response.status_code == HTTPStatus.NOT_FOUND, 'El sistema muestra información ' \
                                                             'de un usuario no existente.'

    def test_ver_usuarios(self, admin_loggeado):
        """
        Prueba el acceso a la lista de usuarios existentes dentro del sistema. \n
        Crea un usuario en la base de datos. \n
        Inicia sesión con este nuevo usuario. \n
        Accede a /usuarios/ .

        Resultado esperado:
            Una respuesta HTTP con código 200

        Mensaje Error:
            No es posible visualizar la lista de usuarios
        """
        response = admin_loggeado.get(reverse('usuarios'))
        assert response.status_code == HTTPStatus.OK, 'No es posible visualizar la lista de usuarios'

    # TODO: Marcos test usuario_asignar_rol_view
    def test_panel_de_administracion_view(self, admin_loggeado):
        """
        Prueba el acceso a la lista de usuarios existentes dentro del sistema. \n
        Crea un usuario en la base de datos. \n
        Inicia sesión con este nuevo usuario. \n
        Accede a /usuarios/ .

        Resultado esperado:
            Una respuesta HTTP con código 200

        Mensaje Error:
            Hubo un error al intentar aceder a la URL del Panel de Control
        """
        response = admin_loggeado.get(reverse('panel_de_control'))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al intentar aceder a la URL del Panel de Control'
    # TODO: Marcos test desasignar_rol_de_sistema_view
