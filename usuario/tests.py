from http import HTTPStatus

import pytest
from django.contrib.auth.models import User, Permission, Group
from django.test import Client
from django.urls import reverse

from roles_de_sistema.models import RolDeSistema
from usuario.models import Usuario


@pytest.fixture
def rs_admin():
    rol = RolDeSistema(nombre='Admin', descripcion='descripcion de prueba')
    rol.save()
    for pp in Permission.objects.filter(content_type__app_label='roles_de_sistema', codename__startswith='p'):
        rol.permisos.add(pp)
    rol.save()
    return rol


@pytest.fixture
def rol_de_sistema():
    rs = RolDeSistema(nombre='RSTest',
                      descripcion='Descripcion del rol')
    rs.save()
    for permiso in Permission.objects.all().filter(codename__startswith='ps_'):
        rs.permisos.add(permiso)
    return rs


@pytest.fixture
def usuario(rs_admin):
    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    user.groups.add(Group.objects.get(name=rs_admin.nombre))
    return user

# Pruebas Unitarias


@pytest.mark.django_db
class TestModeloUsuario:
    """
    Pruebas unitarias que comprueban el funcionamiento de los métodos del Modelo Usuario.
    """

    def test_asignar_rol_a_usuario(self, usuario, rol_de_sistema):
        """
        Prueba unitaria encargada de probar metodo asignar_rol_a_usuario para asegurarse que el \
        rol asignado sea el mismo que le guardado en el usuario.

        Se espera:
            Que el metodo asignar_rol_a_usuario asigne el rol de sistema al usuario.

        Mensaje de Error:
            El rol de sistema no se asignó correctamente
        """
        usuario = Usuario.objects.get(id=usuario.id)
        usuario.asignar_rol_a_usuario(rol_de_sistema.id)
        assert RolDeSistema.objects.get(nombre=usuario.groups.all()[0].name) == rol_de_sistema, \
            'El rol de sistema no se asignó correctamente '

    def test_desasignar_rol_a_usuario(self, usuario, rol_de_sistema):
        """
        Prueba unitaria encargada de probar metodo desasignar_rol_a_usuario para asegurarse que el \
        rol sea correctamente desasignado del usuario.

        Se espera:
            Que el metodo desasignar_rol_a_usuario desasigne el rol de sistema del usuario.

        Mensaje de Error:
            El rol de sistema no se desasignó correctamente
        """
        usuario = Usuario.objects.get(id=usuario.id)
        usuario.desasignar_rol_a_usuario()
        assert len(usuario.groups.all()) == 0, 'El rol de sistema no se desasignó correctamente '

    # TODO: Marcos test get_rol_de_sistema
    # TODO: Marcos test get_permisos_list
    # TODO: Marcos test get_proyectos
    # TODO: Marcos test get_proyectos_activos
    pass


@pytest.mark.django_db
class TestVistasUsuarios:
    """
    Pruebas unitarias que comprueban el funcionamiento de las vistas relacionadas a los Usuarios del Sistema.
    """
    @pytest.fixture
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
    # TODO: Marcos test configurar_cloud_view
