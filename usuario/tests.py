from http import HTTPStatus

import pytest
from django.contrib.auth.models import User, Permission, Group
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante, EstadoDeProyecto
from roles_de_proyecto.models import RolDeProyecto
from roles_de_sistema.models import RolDeSistema
from usuario.models import Usuario


@pytest.fixture
def rs_admin():
    rol = RolDeSistema(nombre='Administrador', descripcion='descripcion de prueba')
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


@pytest.fixture
def gerente(rs_admin):
    user = User(username='gerente', email='gerente@gmail.com')
    user.set_password('password123')
    user.save()
    user.groups.add(Group.objects.get(name=rs_admin.nombre))
    return user


@pytest.fixture
def rol_de_proyecto():
    rol = RolDeProyecto(nombre='Desarrollador', descripcion='Descripcion del rol')
    rol.save()
    rol.asignar_permisos(list(Permission.objects.all().filter(codename__startswith='pp_')))
    return rol


@pytest.fixture
def proyecto(usuario, gerente, rol_de_proyecto):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba', fecha_de_creacion=timezone.now(),
                        gerente=gerente, creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
    proyecto.save()
    participante_gerente = Participante.objects.create(proyecto=proyecto, usuario=gerente)
    participante_gerente.save()
    fase1 = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase1.save()
    fase2 = Fase(nombre='Desarrollo', proyecto=proyecto, fase_anterior=fase1, fase_cerrada=False, puede_cerrarse=False)
    fase2.save()
    fase3 = Fase(nombre='Pruebas', proyecto=proyecto, fase_anterior=fase2, fase_cerrada=False, puede_cerrarse=False)
    fase3.save()
    participante = Participante.objects.create(proyecto=proyecto, usuario=usuario)
    participante.asignar_rol_de_proyecto(rol_de_proyecto)
    participante.save()
    return proyecto
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

    def test_get_rol_de_sistema(self, usuario, rs_admin):
        """
        Prueba unitaria encargada de probar metodo desasignar_rol_a_usuario para asegurarse que el \
        rol sea correctamente desasignado del usuario.

        Se espera:
            Que el metodo desasignar_rol_a_usuario desasigne el rol de sistema del usuario.

        Mensaje de Error:
            El rol de sistema no se desasignó correctamente
        """
        usuario = Usuario.objects.get(id=usuario.id)
        assert usuario.get_rol_de_sistema() == rs_admin, 'El rol de sistema no se trajo correctamente '

    def test_tiene_rs(self, usuario):
        """
        Prueba unitaria encargada de probar metodo tiene_rs para verificar si el \
        usuario tiene algun rol de sistema asignado.

        Se espera:
            Que el metodo tiene_rs returne True si el usuario tiene asignado un Rol de Sistea.

        Mensaje de Error:
            El metodo tiene_rs no esta funcionando correctamente
        """
        usuario = Usuario.objects.get(id=usuario.id)
        assert usuario.tiene_rs(), 'El metodo tiene_rs no esta funcionando correctamente '

    def test_es_administrador(self, usuario):
        """
        Prueba unitaria encargada de probar metodo es_administrador para verificar si \
        el usuario tiene el rol de administrador.

        Se espera:
            Que el metodo es_administrador returne True si el usuario tiene asignado un Rol de Sistea.

        Mensaje de Error:
            El metodo es_administrador no esta funcionando correctamente
        """
        usuario = Usuario.objects.get(id=usuario.id)
        assert usuario.es_administrador(), 'El metodo es_administrador no esta funcionando correctamente '

    def test_get_permisos_list(self, usuario, rs_admin):
        """
        Prueba unitaria encargada de probar metodo get_permisos_list para asegurarse \
        que se traiga correctamente la lista de permisos del usuario.

        Se espera:
            Que el metodo get_permisos_list retorne la lsita de permisos del usuario.

        Mensaje de Error:
            No se trae corectamente la lista de permisos de usuario
        """
        usuario = Usuario.objects.get(id=usuario.id)
        ps_rol = [ps.codename for ps in rs_admin.get_permisos()]
        ps_user = usuario.get_permisos_list()
        assert all(p in ps_rol for p in ps_user) and all(p in ps_user for p in ps_rol), \
            'No se trae corectamente la lista de permisos de usuario '

    def test_get_proyectos(self, usuario, proyecto):
        """
        Prueba unitaria encargada de probar metodo get_proyectos para asegurarse \
        que se traiga correctamente la lista de proyecos en las que está un usuario.

        Se espera:
            Que el metodo get_proyectos retorne la lista de proyecos en las que está un usuario.

        Mensaje de Error:
            No se trae corectamente la lista de proyectos en los que participa el usuario
        """
        usuario = Usuario.objects.get(id=usuario.id)
        user_proyectos = usuario.get_proyectos()
        assert proyecto in user_proyectos and all([p in [proyecto] for p in user_proyectos]), \
            'No se trae corectamente la lista de proyectos en los que participa el usuario '

    def test_get_proyectos_activos(self, usuario, proyecto):
        """
        Prueba unitaria encargada de probar metodo get_proyectos_activos para asegurarse \
        que se traiga correctamente la lista de proyecos activos en las que está un usuario.

        Se espera:
            Que el metodo get_proyectos_activos retorne la lista de proyecos activos en las que está un usuario.

        Mensaje de Error:
            No se trae corectamente la lista de proyectos activos en los que participa el usuario
        """
        usuario = Usuario.objects.get(id=usuario.id)
        user_proyectos = usuario.get_proyectos_activos()
        assert (True if len(user_proyectos) > 0 else proyecto not in user_proyectos), \
            'No se trae corectamente la lista de proyectos activos en los que participa el usuario '
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

    def test_usuario_asignar_rol_view(self, admin_loggeado, usuario):
        """
        Prueba unitaria que se encarga de verificar que la vista \
        usuario_asignar_rol_view se cargue correctamente

        Resultado esperado:
            Una respuesta HTTP con código 200

        Mensaje Error:
            No es posible visualizar la vista de asignacion de rol
        """
        response = admin_loggeado.get(reverse('asignar_rol_de_sistema', args=(usuario.id,)))
        assert response.status_code == HTTPStatus.OK, 'No es posible visualizar la vista de asignacion de rol '

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
