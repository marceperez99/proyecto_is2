import pytest
from django.contrib.auth.models import User, Permission
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante, EstadoDeProyecto, Comite
from roles_de_proyecto.models import RolDeProyecto


@pytest.fixture
def usuario():
    user = User(username='usuario_test', email='usuario@gmail.com')
    user.set_password('password123')
    user.save()
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
    return rol


@pytest.fixture
def proyecto(usuario, gerente, rol_de_proyecto):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba', fecha_de_creacion=timezone.now(),
                        gerente=gerente, creador=usuario)
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
    participante.save()
    return proyecto


@pytest.mark.django_db
@pytest.mark.parametrize('permiso,esperado', [('pp_cerrar_fase', True), ('pp_agregar_items', True)])
def test_participante_tiene_permiso_gerente(proyecto, permiso, esperado):
    gerente = proyecto.get_gerente()
    participante_gerente = Participante.objects.get(usuario=gerente)

    assert participante_gerente.tiene_pp(permiso) == esperado


@pytest.mark.django_db
@pytest.mark.parametrize('permiso,esperado', [('pp_cerrar_fase', False), ('pp_agregar_items', False),
                                              ('pp_agregar_participante', True), ('pp_eliminar_participante', True),
                                              ('pp_asignar_rp_a_participante', True)])
def test_participante_tiene_permiso(usuario, proyecto, rol_de_proyecto, permiso, esperado):
    """
    Prueba unitaria que comprueba el funcionamiento de la funcion tiene_permiso de la clase Participante.
    """
    codename_permisos = [
        'pp_agregar_participante',
        'pp_eliminar_participante',
        'pp_asignar_rp_a_participante'
    ]
    rol_de_proyecto.asignar_permisos([Permission.objects.get(codename=codename) for codename in codename_permisos])
    participante = Participante.objects.get(usuario=usuario)

    participante.asignar_rol_de_proyecto(rol_de_proyecto)
    valor_prueba = participante.tiene_pp(permiso)
    assert valor_prueba == esperado, f'Se espera que la verificacion de si el participante tiene el Permiso ' + \
                                     f'{permiso} resulte en {esperado}, pero resulto {valor_prueba}'

@pytest.mark.django_db
def test_cancelar_proyecto_en_configuracion(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de cancelar un proyecto con estado "En Configuracion", este quede
    con estado "Cancelado".

    Se espera:
        Que el proyecto quede en estado "Cancelado".

    Mensaje de error:
        No se pudo Cancelar el Proyecto.
    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=timezone.now(),
                               creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
    proyecto_prueba.save()
    proyecto_prueba.cancelar()
    assert proyecto_prueba.estado == EstadoDeProyecto.CANCELADO, "No se pudo Cancelar el Proyecto"


@pytest.mark.django_db
def test_cancelar_proyecto_iniciado(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de cancelar un proyecto con estado "Iniciado", este quede con
    estado "Cancelado".

    Se espera:
        Que el proyecto quede en estado "Cancelado".

    Mensaje de error:
        No se pudo Cancelar el Proyecto.
    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=timezone.now(),
                               creador=usuario, estado=EstadoDeProyecto.INICIADO)
    proyecto_prueba.save()
    proyecto_prueba.cancelar()
    assert proyecto_prueba.estado == EstadoDeProyecto.CANCELADO, "No se pudo Cancelar el Proyecto"


@pytest.mark.django_db
def test_cancelar_proyecto_finalizado(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de cancelar un proyecto con estado "Finalizadp", este no
    le permita cambiar su estado.

    Se espera:
        Que el proyecto siga con el estado "Finalizado".

    Mensaje de error:
        No se pudo Cancelar un Proyecto con estado "Finalizado".
    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=timezone.now(),
                               creador=usuario, estado=EstadoDeProyecto.FINALIZADO)
    proyecto_prueba.save()
    proyecto_prueba.cancelar()
    assert proyecto_prueba.estado == EstadoDeProyecto.FINALIZADO, "No se puede cambiar el estado de un proyecto con estado Finalizado"


@pytest.mark.django_db
def test_iniciar_proyecto_en_configuracion_sin_fases(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de iniciar un proyecto sin fases con un estado "En Configuracion",
    este no cambie su estado.

    Se espera:
        Que el proyecto no cambie de estado.

    Mensaje de error:
        No se puede Iniciar el Proyecto sin fases.
    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=timezone.now(),
                               creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
    comite = Comite(proyecto=proyecto_prueba)
    proyecto_prueba.save()
    comite.save()
    proyecto_prueba.iniciar()
    assert proyecto_prueba.estado == EstadoDeProyecto.CONFIGURACION, 'No se puede Iniciar el Proyecto sin fases'


@pytest.mark.django_db
def test_iniciar_proyecto_en_configuracion(usuario, rol_de_proyecto):
    """
    Prueba unitaria para verificar que al momento de iniciar un proyecto con al menos una fase y un comite de cambios,
    este cambie de estado "En Configuracion", a "Iniciado".

    Se espera:
        Que el proyecto cambie a estado "Iniciado".

    Mensaje de error:
        No se puede iniciar el Proyecto.
    """
    proyecto_prueba = Proyecto(nombre='IS2', descripcion='Descripcion', fecha_de_creacion=timezone.now(),
                               creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
    proyecto_prueba.save()

    user1 = User(username='usuario_1', email='usuario1@gmail.com')
    user1.set_password('password123')
    user1.save()
    user2 = User(username='usuario_2', email='usuario2@gmail.com')
    user2.set_password('password123')
    user2.save()
    user3 = User(username='usuario_3', email='usuario3@gmail.com')
    user3.set_password('password123')
    user3.save()
    participante1 = Participante(proyecto=proyecto_prueba, usuario=user1)
    participante1.save()
    participante2 = Participante(proyecto=proyecto_prueba, usuario=user2)
    participante2.save()
    participante3 = Participante(proyecto=proyecto_prueba, usuario=user3)
    participante3.save()
    comite = Comite(proyecto=proyecto_prueba)
    comite.save()
    comite.miembros.add(participante1, participante2, participante3)
    comite.save()

    fase_1 = Fase(nombre='Analisis', proyecto=proyecto_prueba, fase_cerrada=False, puede_cerrarse=False)
    fase_1.fase_anterior = None
    fase_1.save()
    proyecto_prueba.iniciar()
    assert proyecto_prueba.estado == EstadoDeProyecto.INICIADO, 'No se puede iniciar el Proyecto'
