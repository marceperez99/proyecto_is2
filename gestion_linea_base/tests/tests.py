import pytest
from http import HTTPStatus
from django.urls import reverse

from gestion_de_fase.models import Fase
from gestion_de_proyecto.tests.factories import proyecto_factory
from gestion_linea_base.models import LineaBase
from roles_de_proyecto.tests.factories import rol_de_proyecto_factory
from roles_de_sistema.tests.factories import rol_de_sistema_factory
from usuario.tests.factories import user_factory
from django.test import Client
import gestion_de_solicitud.tests.test_case as tc


@pytest.fixture
def rs_admin():
    return rol_de_sistema_factory(tc.admin['nombre'], tc.admin['descripcion'], tc.admin['permisos'])


@pytest.fixture
def usuario1(rs_admin):
    return user_factory(tc.user['username'], tc.user['password'], tc.user['email'],
                        tc.user['rol_de_sistema'])


@pytest.fixture
def usuario2(rs_admin):
    return user_factory(tc.user2['username'], tc.user2['password'], tc.user2['email'],
                        tc.user2['rol_de_sistema'])


@pytest.fixture
def gerente(rs_admin):
    return user_factory(tc.gerente['username'], tc.gerente['password'], tc.gerente['email'],
                        tc.gerente['rol_de_sistema'])


@pytest.fixture
def rol_de_proyecto():
    return rol_de_proyecto_factory(tc.rol_de_proyecto)


@pytest.fixture
def proyecto(usuario1, usuario2, gerente, rol_de_proyecto):
    return proyecto_factory(tc.proyecto)


@pytest.fixture
def fase(usuario1, usuario2, gerente, rol_de_proyecto, proyecto):
    return Fase.objects.get(nombre='Fase 1')


@pytest.fixture
def linea_base(usuario1, usuario2, gerente, rol_de_proyecto, proyecto):
    return LineaBase.objects.get(nombre='LB_1.1')


class TestModeloLineaBase:
    pass


@pytest.mark.django_db
class TestVistasLineasBase:

    @pytest.fixture
    def cliente_loggeado(self, gerente):
        client = Client()
        client.login(username=tc.gerente['username'], password=tc.gerente['password'])
        return client

    def test_solicitar_rompimiento_view(self, cliente_loggeado, proyecto, fase, linea_base):
        """
        Prueba unitaria que verifica que la vista solicitar_rompimiento_view.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """

        response = cliente_loggeado.get(
            reverse('solicitar_rompimiento', args=(proyecto.id, fase.id, linea_base.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'

    # TODO: Marcos test_nueva_linea_base_view
    # TODO: Marcos test_listar_linea_base_view
    # TODO: Marcos test_visualizar_linea_base_view
    pass
