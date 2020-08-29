import pytest
from django.contrib.auth.models import Permission, User, Group
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, EstadoDeProyecto, Participante
from gestion_de_tipo_de_item.models import TipoDeItem
from roles_de_proyecto.models import RolDeProyecto
from roles_de_sistema.models import RolDeSistema
from gestion_de_solicitud.models import SolicitudDeCambio, EstadoSolicitud
from gestion_linea_base.models import LineaBase
from gestion_de_solicitud.utils import cancelar_solicitud


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
    user = User(username='usuario_test', email='usuario@gmail.com')
    user.set_password('password123')
    user.save()
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
def proyecto(usuario, gerente):
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
    return proyecto


@pytest.fixture
def participante(proyecto, usuario, rol_de_proyecto):
    participante = Participante.objects.create(proyecto=proyecto, usuario=usuario)
    participante.asignar_rol_de_proyecto(rol_de_proyecto)
    participante.save()
    return participante


@pytest.fixture
def tipo_de_item(usuario, proyecto):
    tipo_de_item = TipoDeItem()
    tipo_de_item.nombre = "Requerimiento Funcional"
    tipo_de_item.descripcion = "Especificación de un requerimiento funcional."
    tipo_de_item.prefijo = "RF"
    tipo_de_item.creador = usuario
    tipo_de_item.fase = Fase.objects.get(nombre='Analisis')
    tipo_de_item.fecha_creacion = timezone.now()
    tipo_de_item.save()
    return tipo_de_item

@pytest.fixture
def linea_base(tipo_de_item):
    lb = LineaBase(nombre="LB_1.1", estado='')
    lb.save()
    return lb


@pytest.fixture
def solicitud(linea_base, participante):
    solicitud = SolicitudDeCambio(numero_de_miembros=0, estado=EstadoSolicitud.PENDIENTE, linea_base=linea_base,
                                  solicitante=participante)

    solicitud.save()
    return solicitud


@pytest.mark.django_db
class TestUtils:

    def test_cancelar_solicitud(self, proyecto):
        """
        TODO: marcelo incluir en planilla de control de documetnacion y pruebas
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
        TODO: marcelo incluir en planilla de control de documetnacion y pruebas
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

        assert True