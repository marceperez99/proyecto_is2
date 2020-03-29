from django.test import TestCase
from django.test import TestCase

import pytest
from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.utils import timezone

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
def test_iniciar_proyecto_en_configuracion_sin_fases(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de iniciar un proyecto sin fases con un estado "En Configuracion", este no cambie su estado
    Se espera:\n
        Que el proyecto no cambie de estado.\n
    Mensaje de error:
        No se puede Iniciar el Proyecto sin fases.\n
    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=timezone.now(),
                               creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
    proyecto_prueba.save()
    proyecto_prueba.iniciar()
    assert proyecto_prueba.estado == EstadoDeProyecto.CONFIGURACION, 'No se puede Iniciar el Proyecto sin fases'



@pytest.mark.django_db
def test_iniciar_proyecto_en_configuracion_con_fases(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de iniciar un proyecto con al menos una fase, este cambie de estado "En Configuracion",
    a "Iniciado".\n
    Se espera:\n
        Que el proyecto cambie a estado "Iniciado".\n
    Mensaje de error:
        No se puede iniciar el Proyecto.\n
    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=timezone.now(),
                               creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
    proyecto_prueba.save()
    fase_1 = Fase(nombre='Analisis', proyecto=proyecto_prueba, fase_cerrada=False, puede_cerrarse=False)
    fase_1.fase_anterior = None
    fase_1.save()
    proyecto_prueba.iniciar()
    assert proyecto_prueba.estado == EstadoDeProyecto.INICIADO, 'No se puede iniciar el Proyecto'








