import pytest

from gestion_de_item.models import EstadoDeItem
from gestion_de_proyecto.tests.factories import proyecto_factory
from roles_de_proyecto.tests.factories import rol_de_proyecto_factory
from gestion_de_solicitud.models import EstadoSolicitud, SolicitudDeCambio
from gestion_de_solicitud.utils import cancelar_solicitud, aprobar_solicitud
from roles_de_sistema.tests.factories import rol_de_sistema_factory
import gestion_de_solicitud.tests.test_case as tc
from usuario.tests.factories import user_factory


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


@pytest.mark.django_db
class TestUtils:

    def test_cancelar_solicitud(self, proyecto):
        """
        Prueba unitaria que prueba el proceso llevado a cabo al cancelar una solicitud de ruptura del LB.
        Resultado esperado:
            La solicitud de cambio pase al estado 'Rechazada'.
        Mensajes de error:
            - No se cancelo la solicitud correctamente
        """
        solicitud = SolicitudDeCambio.objects.get(linea_base__nombre='LB_1.1')
        cancelar_solicitud(solicitud)
        assert solicitud.estado == EstadoSolicitud.RECHAZADA, 'No se cancelo la solicitud correctamente'

    @pytest.mark.parametrize('solicitud', ['LB_1.1', 'LB_1.2', 'LB_2.1', 'LB_3.1'])
    def test_aceptar_solicitud(self, proyecto, solicitud):
        """
        Prueba unitaria que prueba el proceso llevado a cabo al aprobar una solicitud de ruptura del LB.
        Resultado esperado:
            La solicitud de cambio pase al estado 'Aprobada'.

        Mensajes de error:
            - El estado de la Solicitud deberia parar a Aprobada.
            - Existen items que estan en estado A Modificar pero no estaban incluidos en la Solicitud.
            - Solo los items que previamente estaban en Linea Base o Aprobados pasan al estado En Revision.
            - Los hijos o sucesores de un item a modificar no pueden quedar en los estados
            En Linea Base, Aprobado o A Aprobar.
            - Existen items que deberian estan en Revision y no lo estan.
        """
        solicitud = SolicitudDeCambio.objects.get(linea_base__nombre=solicitud)
        aprobar_solicitud(solicitud)
        solicitud.refresh_from_db()

        assert solicitud.estado == EstadoSolicitud.APROBADA, \
            f'El estado de la Solicitud deberia parar a Aprobada'

        # Se verifican los items que estaban en la linea base
        for item in solicitud.linea_base.items.all():
            # Si el item se encontraba en los que se deberia modificar
            if item.estado == EstadoDeItem.A_MODIFICAR:
                assert solicitud.asignacion_set.filter(item=item).exists(), f'Existen items que estan en estado ' \
                                                                            f'A Modificar pero no estaban incluidos ' \
                                                                            f'en la Solicitud'
                # se verifican los hijos de los items a modificar
                for hijo in item.hijos.all():
                    hijo = hijo.item
                    if hijo.estado == EstadoDeItem.EN_REVISION:
                        assert hijo.estado_anterior in [EstadoDeItem.EN_LINEA_BASE, EstadoDeItem.APROBADO], \
                            'Solo los items que previamente estaban en Linea Base o Aprobados pasan al estado' \
                            'En Revision'
                    assert hijo.estado not in [EstadoDeItem.EN_LINEA_BASE, EstadoDeItem.APROBADO,
                                               EstadoDeItem.A_APROBAR], \
                        'Los hijos o sucesores de un item a modificar no pueden quedar en los estados ' \
                        'En Linea Base, Aprobado o A Aprobar'
                # se verifican los sucesores de los items a modificar
                for sucesor in item.sucesores.all():
                    sucesor = sucesor.item
                    if sucesor.estado == EstadoDeItem.EN_REVISION:
                        assert sucesor.estado_anterior in [EstadoDeItem.EN_LINEA_BASE, EstadoDeItem.APROBADO], \
                            'Solo los items que previamente estaban en Linea Base o Aprobados pasan al estado' \
                            'En Revision'
                    assert sucesor.estado not in [EstadoDeItem.EN_LINEA_BASE, EstadoDeItem.APROBADO,
                                                  EstadoDeItem.A_APROBAR], \
                        'Los hijos o sucesores de un item a modificar no pueden quedar en los estados ' \
                        'En Linea Base, Aprobado o A Aprobar'

            else:
                assert item.estado == EstadoDeItem.EN_REVISION, 'Existen items que deberian estan en Revision y no lo' \
                                                                'estan'


@pytest.mark.django_db
class TestModeloSolicitudDeCambio:
    @pytest.mark.parametrize('solicitud, nro_votos', [('LB_1.1', 3), ('LB_1.2', 1)])
    def test_get_votos_a_favor(self, proyecto, solicitud, nro_votos):
        """
        Prueba unitaria que comprueba funcionamiento del metodo get_votos_a_favor.

        Se espera:

            - Que el metodo retorne correctamente el numero de votos a favor que tiene una solicitud.
        Mensaje de error:
            - No se retornó correctamente el numero de votos a favor, se esperaba {nro_votos} pero se retornó {votos}

        """
        solicitud = SolicitudDeCambio.objects.get(linea_base__nombre=solicitud)
        votos = solicitud.get_votos_a_favor()

        assert votos == nro_votos, f"No se retornó correctamente el numero de votos a favor, se esperaba {nro_votos} " \
                                   f"pero se retornó {votos}"
