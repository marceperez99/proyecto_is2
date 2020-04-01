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
from datetime import datetime


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
def test_vista_crear_rol_usuario_loggeado(usuario, cliente_loggeado, rs_admin):
    """
    Test encargado de comprobar que no ocurra nigun error al cargar la pagina con un usuario que ha iniciado sesion
    """
    usuario.groups.add(Group.objects.get(name=rs_admin.nombre))
    response = cliente_loggeado.get(reverse('nuevo_rol_de_proyecto'))

    assert response.status_code == HTTPStatus.OK, 'Hubo un error al cargar la pagina, '


@pytest.mark.django_db
def test_roldeproyecto_lista_de_permisos():
    """
    Prueba unitaria encargada de probar metodo get_permisos para asegurarse que al tratar de obtener los permisos de un
    rol creado retorne una lista con esos
    """
    permisos = list(Permission.objects.all())
    rol = RolDeProyecto(nombre='rol1', descripcion="descripcion")
    rol.save()
    rol.permisos.set(permisos)

    permisos_obtenidos = rol.get_permisos()

    assert permisos_obtenidos == permisos, "Los permisos asignados al rol no fueron guardados correctamente"


@pytest.mark.django_db
def test_roldeproyecto_lista_de_permisos_vacia():
    """
    Prueba unitaria encargada de probar metodo get_permisos para asegurarse que al tratar de obtener los permisos de un
    rol creado sin permisos retorne una lista vacia
    """
    rol = RolDeProyecto(nombre='rol1', descripcion="descripcion")
    rol.save()

    permisos_obtenidos = rol.get_permisos()

    assert permisos_obtenidos == [], "Los permisos asignados al rol no fueron guardados correctamente, "


@pytest.mark.django_db
def test_asignar_rol_de_proyecto(proyecto, usuario, rol_de_proyecto):
    """
    Prueba que verifica la asignacion correcta de un rol de proyecto a un usuario.
    """
    permisos = list(rol_de_proyecto.permisos.all())
    fases = list(Fase.objects.all().filter(proyecto=proyecto))
    permisos_por_fase = {fases[0]: permisos}
    print(proyecto.participante_set.all()[0].usuario == usuario)
    proyecto.asignar_rol_de_proyecto(usuario, rol_de_proyecto, permisos_por_fase)
    # Comprobacion de postcondicion
    condicion = proyecto.participante_set.get(usuario=usuario).rol == rol_de_proyecto
    condicion = condicion and proyecto.participante_set.get(usuario=usuario).permisos_por_fase.all().exists()
    assert condicion is True, 'El rol no ha sido asignado al participante o no se han asignado los permisos ' \
                              'correspondientes al participante'


@pytest.mark.django_db
def test_get_participantes(proyecto):
    """
    Prueba unitaria encargada de verificar que la funcion get_participantes retorne correctamente los participantes
    de un proyecto.
    """

    participantes = list(Participante.objects.all().filter(proyecto=proyecto))
    gerente = proyecto.participante_set.get(usuario=proyecto.gerente)
    assert list(proyecto.get_participantes()) == [gerente], 'No se retornaron correctamente los participantes del' \
                                                                'Proyecto'


@pytest.mark.django_db
def test_tiene_permiso_de_proyecto(proyecto, usuario, rol_de_proyecto):
    """
    Test que verifica que el metodo tiene_permiso_de_proyecto de la clase Proyecto retorne verdadero si el
    usuario no cuenta con el permiso dado.
    """
    fases = proyecto.fase_set.all()
    permisos = list(rol_de_proyecto.get_pp_por_fase())
    permisos_por_fase = {fases[0]: permisos}
    proyecto.asignar_rol_de_proyecto(usuario, rol_de_proyecto, permisos_por_fase)

    condicion = proyecto.tiene_permiso_de_proyecto(usuario, 'pp_agregar_participante')
    assert condicion is True, 'El usuario cuenta con el permiso de proyecto pero no se encuentra este'


@pytest.mark.django_db
def test_tiene_no_permiso_de_proyecto(proyecto, usuario, rol_de_proyecto):
    """
    Test que verifica que el metodo tiene_permiso_de_proyecto de la clase Proyecto retorne falso si el
    usuario no cuenta con el permiso dado.
    """
    fases = Fase.objects.all().filter(proyecto=proyecto)
    permisos = list(rol_de_proyecto.get_pp_por_fase())
    permisos_por_fase = {fases[0]: permisos}
    proyecto.asignar_rol_de_proyecto(usuario, rol_de_proyecto, permisos_por_fase)

    condicion = proyecto.tiene_permiso_de_proyecto(usuario, 'pp_permiso_no_existente')
    assert condicion is False, 'El usuario cuenta con el permiso de proyecto pero no se encuentra este'
