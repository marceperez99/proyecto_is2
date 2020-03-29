import pytest
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante
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
