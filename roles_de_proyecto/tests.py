from http import HTTPStatus
import pytest
from django.contrib.auth.models import Permission, User, Group
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante
from roles_de_sistema.models import RolDeSistema
from .models import RolDeProyecto


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
def usuario():
    user = User(username='user_test', email='test@admin.com')
    user.set_password('password123')
    user.save()
    return user


@pytest.fixture
def cliente_loggeado(usuario):
    client = Client()
    client.login(username='user_test', password='password123')
    return client


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
    # TODO: asignar_permisos
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

    # TODO: Marcelo test es_utilizado
    # TODO: Marcelo test tiene_pp
    # TODO: Marcelo test get_pp_por_proyecto
    # TODO: Marcelo test get_pp_por_fase

    pass


@pytest.mark.django_db
class TestVistasRolDeProyecto:
    def test_nuevo_rol_de_proyecto_view(self, usuario, cliente_loggeado, rs_admin):
        """
        Test encargado de comprobar que no ocurra nigun error al cargar la pagina con un usuario que ha iniciado sesion.

        Se espera:
            Status code de la respuesta del servidor 300.

        Mensaje de Error:
            No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        usuario.groups.add(Group.objects.get(name=rs_admin.nombre))
        response = cliente_loggeado.get(reverse('nuevo_rol_de_proyecto'))

        assert response.status_code == HTTPStatus.OK, 'No se obtuvo la pagina correctamente. Se esperaba un status code 300'
    # TODO: Marcelo test listar_roles_de_proyecto_view
    # TODO: Marcelo test editar_rol_de_proyecto_view
    # TODO: Marcelo test rol_de_proyecto_view
    # TODO: Marcelo test eliminar_rol_de_proyecto_view
    pass
