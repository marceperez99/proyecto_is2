from datetime import datetime
import pytest
from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante, EstadoDeProyecto
from roles_de_proyecto.models import RolDeProyecto


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
def rol_de_proyecto():
    rol = RolDeProyecto(nombre='Desarrollador', descripcion='Descripcion del rol')
    rol.save()
    rol.asignar_permisos(list(Permission.objects.all().filter(codename__startswith='pp_')))
    return rol



@pytest.mark.django_db
def test_cancelar_proyecto_en_configuracion(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de cancelar un proyecto con estado "En Configuracion", este quede con estado "Cancelado".
    Se espera:\n
        Que el proyecto quede en estado "Cancelado".\n
    Mensaje de error:
        No se pudo Cancelar el Proyecto.\n

    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=datetime.today(),
                               creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
    proyecto_prueba.save()
    proyecto_prueba.cancelar()
    assert proyecto_prueba.estado == EstadoDeProyecto.CANCELADO, "No se pudo Cancelar el Proyecto"



@pytest.mark.django_db
def test_cancelar_proyecto_iniciado(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de cancelar un proyecto con estado "Iniciado", este quede con estado "Cancelado".
    Se espera:\n
        Que el proyecto quede en estado "Cancelado".\n
    Mensaje de error:
        No se pudo Cancelar el Proyecto.\n

    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=datetime.today(),
                               creador=usuario, estado=EstadoDeProyecto.INICIADO)
    proyecto_prueba.save()
    proyecto_prueba.cancelar()
    assert proyecto_prueba.estado == EstadoDeProyecto.CANCELADO, "No se pudo Cancelar el Proyecto"


@pytest.mark.django_db
def test_cancelar_proyecto_finalizado(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de cancelar un proyecto con estado "Finalizadp", este no
    le permita cambiar su estado.
    Se espera:\n
        Que el proyecto siga con el estado "Finalizado".\n
    Mensaje de error:
        No se pudo Cancelar un Proyecto con estado "Finalizado".\n

    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=datetime.today(),
                               creador=usuario, estado=EstadoDeProyecto.FINALIZADO)
    proyecto_prueba.save()
    proyecto_prueba.cancelar()
    assert proyecto_prueba.estado == EstadoDeProyecto.FINALIZADO, "No se puede cambiar el estado de un proyecto con estado Finalizado"




