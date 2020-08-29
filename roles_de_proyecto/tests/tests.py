from http import HTTPStatus
import pytest
from django.contrib.auth.models import Permission, User, Group
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante
from roles_de_sistema.models import RolDeSistema
from roles_de_proyecto.models import RolDeProyecto


# FIXTURES

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
    user = User(username='user_test', email='test@admin.com')
    user.set_password('password123')
    user.save()
    user.groups.add(Group.objects.get(name=rs_admin.nombre))
    return user


@pytest.fixture
def gerente():
    user = User(username='gerente', email='gerente@gmail.com')
    user.set_password('password123')
    user.save()
    return user


@pytest.fixture
def rol_de_proyecto():
    rol = RolDeProyecto(nombre='Desarrollador', descripcion='Descripcion del rol')
    rol.save()
    rol.asignar_permisos(list(Permission.objects.all().filter(codename__startswith='pp_')))
    return rol


@pytest.fixture
def proyecto(usuario, gerente, rol_de_proyecto):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba',
                        fecha_de_creacion=timezone.now(),
                        creador=usuario, gerente=gerente)
    proyecto.save()
    fase = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    fase = Fase(nombre='Desarrollo', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    fase = Fase(nombre='Pruebas', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()

    participante = Participante.objects.create(proyecto=proyecto, usuario=gerente)
    participante.save()

    participante = Participante.objects.create(proyecto=proyecto, usuario=usuario)
    participante.save()
    return proyecto


# Pruebas Unitarias
@pytest.mark.django_db
class TestModeloRolDeProyecto:
    """
    Pruebas unitarias que comprueban el funcionamiento de los métodos del Modelo RolDeProyecto.
    """

    def test_roldeproyecto_lista_de_permisos(self):
        """
        Prueba unitaria encargada de probar metodo get_permisos para asegurarse que al tratar de obtener los permisos de un
        rol creado retorne una lista con esos.

        Se espera:
            Que la lista de permisos obtenida por get_permisos sea la misma que se asignó al rol.

        Mensaje de Error:
            Los permisos asignados al rol no fueron guardados correctamente.
        """
        permisos = list(Permission.objects.all())
        rol = RolDeProyecto(nombre='rol1', descripcion="descripcion")
        rol.save()
        rol.permisos.set(permisos)

        permisos_obtenidos = rol.get_permisos()

        assert permisos_obtenidos == permisos, "Los permisos asignados al rol no fueron guardados correctamente"

    def test_roldeproyecto_lista_de_permisos_vacia(self):
        """
        Prueba unitaria encargada de probar metodo get_permisos para asegurarse que al tratar de obtener los permisos de un
        rol creado sin permisos retorne una lista vacia.

        Se espera:
            Que la lista de permisos obtenidas por get_permisos esté vacía.

        Mensaje de Error:
            Los permisos asignados al rol no fueron guardados correctamente, se esperaba obtener una lista vacía.
        """
        rol = RolDeProyecto(nombre='rol1', descripcion="descripcion")
        rol.save()

        permisos_obtenidos = rol.get_permisos()

        assert permisos_obtenidos == [], "Los permisos asignados al rol no fueron guardados correctamente, se esperaba" \
                                         " obtener una lista vacía"

    @pytest.mark.parametrize('rol, esperado', [('rol1', True), ('rol2', False)])
    def test_es_utilizado(self, proyecto, usuario, rol, esperado):
        """
        Prueba unitaria encargada de comprobar el funcionamiento del método es_utilizado del Modelo Rol de Proyecto.

        La prueba crea dos roles de proyecto y asigna uno de los roles a un usuario en un proyecto. Luego se comprueba
        sobre cada uno de los roles si es utilizado o no.

        Se espera:
            Que el metodo es_utilizado retorne para los roles:
                'rol1' -> True\n
                'rol2' -> False

        Mensaje de Error:
            Se esperaba que el metodo retorne {esperado} para el rol {rol}
        """
        permisos = Permission.objects.filter(codename__startswith='pp_')
        roles = [RolDeProyecto.objects.create(nombre='rol1', descripcion=" "),
                 RolDeProyecto.objects.create(nombre='rol2', descripcion=" ")]
        map(lambda r: r.permisos.add(*permisos), roles)
        proyecto.asignar_rol_de_proyecto(usuario, roles[0], {})

        rol = RolDeProyecto.objects.get(nombre=rol)
        condicion = rol.es_utilizado() == esperado
        assert condicion is True, f'Se esperaba que el metodo retorne {esperado} para el rol {rol}'

    @pytest.mark.parametrize('permiso, esperado', [('pp_f_crear_tipo_de_item', True), ('pp_ver_participante', False)])
    def test_tiene_pp(self, permiso, esperado):
        """
        Prueba unitaria encargada de comprobar el funcionamiento del método tiene_pp del Modelo Rol de Proyecto.

        La prueba crea un rol de Proyecto al que le asigna todos los permisos de proyecto que se utilizan dentro de las
        fase.

        Se espera:
            Que el metodo es_utilizado retorne para los roles:
                'pp_f_crear_tipo_de_item' -> True\n
                'rol2' -> False

        Mensaje de Error:
            Se esperaba que el metodo tiene_pp retorne {esperado} al consultar por el permiso {permiso}
        """
        permisos = Permission.objects.filter(codename__startswith='pp_f')
        rol = RolDeProyecto.objects.create(nombre='rol1', descripcion=" ")
        rol.permisos.add(*permisos)

        condicion = rol.tiene_pp(permiso) == esperado
        assert condicion is True, f'Se esperaba que el metodo tiene_pp retorne {esperado} ' \
                                  f'al consultar por el permiso {permiso}'

    # TODO: Marcelo test get_pp_por_proyecto
    def test_get_pp_por_proyecto(self):
        """
        Prueba unitaria encargada de comprobar el funcionamiento del método get_pp_por_proyecto
        del Modelo Rol de Proyecto.

        La prueba crea un Rol de Proyecto y le asigna todos los los permisos de proyecto.

        Se espera:
            Que el metodo get_pp_por_proyecto retorne la lista de permisos que son aplicables al proyecto en general.

        Mensaje de Error:
            El método no retornó correctamente la lista de permisos de proyecto
        """
        permisos = Permission.objects.filter(codename__startswith='pp_')
        rol = RolDeProyecto.objects.create(nombre='rol1', descripcion=" ")
        rol.permisos.add(*permisos)
        permisos = [p.codename for p in permisos if not p.codename.startswith('pp_f_')]

        permisos_obtenidos = rol.get_pp_por_proyecto()
        permisos_obtenidos = [pp.codename for pp in permisos_obtenidos]
        condicion = all(p in permisos for p in permisos_obtenidos) and all(p in permisos_obtenidos for p in permisos)

        assert condicion is True, f'El método no retornó correctamente la lista de permisos de proyecto, ' \
                                  f'se retornó {permisos_obtenidos} y se esperaba {permisos}'

    # TODO: Marcelo test get_pp_por_fase
    def test_get_pp_por_fase(self):
        """
        Prueba unitaria encargada de comprobar el funcionamiento del método get_pp_por_fase
        del Modelo Rol de Proyecto.

        La prueba crea un Rol de Proyecto y le asigna todos los los permisos de proyecto.

        Se espera:
            Que el metodo get_pp_por_proyecto retorne la lista de permisos que son aplicables solo dentro de cada fase
            del proyecto.

        Mensaje de Error:
            El método no retornó correctamente la lista de permisos de proyecto
        """
        permisos = Permission.objects.filter(codename__startswith='pp_')
        rol = RolDeProyecto.objects.create(nombre='rol1', descripcion=" ")
        rol.permisos.add(*permisos)
        permisos = [p.codename for p in permisos if p.codename.startswith('pp_f_')]

        permisos_obtenidos = rol.get_pp_por_fase()
        permisos_obtenidos = [pp.codename for pp in permisos_obtenidos]
        condicion = all(p in permisos for p in permisos_obtenidos) and all(p in permisos_obtenidos for p in permisos)

        assert condicion is True, f'El método no retornó correctamente la lista de permisos de proyecto, ' \
                                  f'se retornó {permisos_obtenidos} y se esperaba {permisos}'

    pass


@pytest.mark.django_db
class TestVistasRolDeProyecto:
    """
    Pruebas unitarias que comprueban el funcionamiento de las vistas referentes a los Roles de Proyecto.
    """

    @pytest.fixture
    def cliente_loggeado(self, usuario):
        client = Client()
        client.login(username='user_test', password='password123')
        return client

    def test_nuevo_rol_de_proyecto_view(self, usuario, cliente_loggeado, rs_admin):
        """
        Test encargado de comprobar que no ocurra nigun error al cargar la pagina con un usuario que ha iniciado sesion.

        Se espera:
            Status code de la respuesta del servidor 300.

        Mensaje de Error:
            No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """

        response = cliente_loggeado.get(reverse('nuevo_rol_de_proyecto'))

        assert response.status_code == HTTPStatus.OK, 'No se obtuvo la pagina correctamente. ' \
                                                      'Se esperaba un status code 300'

    def test_listar_roles_de_proyecto_view(self, usuario, cliente_loggeado, rs_admin):
        """
        Test encargado de comprobar que no ocurra nigun error al cargar la vista donde se listan los roles de
        Proyecto.

        Se espera:
            Status code de la respuesta del servidor 300.

        Mensaje de Error:
            No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """

        response = cliente_loggeado.get(reverse('listar_roles_de_proyecto'))

        assert response.status_code == HTTPStatus.OK, 'No se obtuvo la pagina correctamente. ' \
                                                      'Se esperaba un status code 300'

    def test_editar_rol_de_proyecto_view(self, cliente_loggeado, rol_de_proyecto):
        """
        Test encargado de comprobar que no ocurra nigun error al cargar la vista de edición de un rol de Proyecto.

        Se espera:
            Status code de la respuesta del servidor 300.

        Mensaje de Error:
            No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        response = cliente_loggeado.get(reverse('editar_rol_de_proyecto', args=(rol_de_proyecto.id,)))

        assert response.status_code == HTTPStatus.OK, 'No se obtuvo la pagina correctamente. ' \
                                                      'Se esperaba un status code 300'

    def test_rol_de_proyecto_view(self, cliente_loggeado, rol_de_proyecto):
        """
        Test encargado de comprobar que no ocurra nigun error al cargar la vista de un rol de Proyecto.

        Se espera:
            Status code de la respuesta del servidor 300.

        Mensaje de Error:
            No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        response = cliente_loggeado.get(reverse('rol_de_proyecto', args=(rol_de_proyecto.id,)))

        assert response.status_code == HTTPStatus.OK, 'No se obtuvo la pagina correctamente. ' \
                                                      'Se esperaba un status code 300'

    def test_eliminar_rol_de_proyecto_view(self, cliente_loggeado, rol_de_proyecto):
        """
        Test encargado de comprobar que no ocurra nigun error al cargar la vista de eliminación de un rol de Proyecto.

        Se espera:
            Status code de la respuesta del servidor 300.

        Mensaje de Error:
            No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        response = cliente_loggeado.get(reverse('eliminar_rol_de_proyecto', args=(rol_de_proyecto.id,)))

        assert response.status_code == HTTPStatus.OK, 'No se obtuvo la pagina correctamente. ' \
                                                      'Se esperaba un status code 300'
