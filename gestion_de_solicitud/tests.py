import pytest
from django.contrib.auth.models import Permission, User, Group
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, EstadoDeProyecto, Participante
from roles_de_proyecto.models import RolDeProyecto
from roles_de_sistema.models import RolDeSistema
from .models import SolicitudDeCambio, EstadoSolicitud
from gestion_linea_base.models import LineaBase
from .utils import cancelar_solicitud


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
def linea_base():
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

    def test_cancelar_solicitud(self, solicitud):
        resultado = cancelar_solicitud(solicitud)

        assert resultado, 'No se cancelo la solicitud correctamente'
