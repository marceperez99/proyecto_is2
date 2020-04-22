from http import HTTPStatus

import pytest
from django.contrib.auth.models import User, Permission, Group
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Participante, Proyecto
from roles_de_proyecto.models import RolDeProyecto
from roles_de_sistema.models import RolDeSistema


@pytest.fixture
def rs_admin():
    rol = RolDeSistema(nombre='Admin', descripcion='descripcion de prueba')
    rol.save()
    for pp in Permission.objects.filter(content_type__app_label='roles_de_sistema', codename__startswith='p'):
        rol.permisos.add(pp)
    rol.save()
    return rol


@pytest.fixture
def usuario(rs_admin):
    user = User(username='user_test', email='test@admin.com')
    user.set_password('password123')
    user.save()
    user.groups.add(Group.objects.get(name=rs_admin.nombre))
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


@pytest.fixture
def proyecto(usuario):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba',
                        creador=usuario, gerente=usuario, fecha_de_creacion=timezone.now())
    proyecto.save()
    participante = Participante.objects.create(proyecto=proyecto, usuario=usuario)
    participante.save()
    return proyecto


@pytest.fixture()
def fase(proyecto):
    fase = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    fase = Fase(nombre='Desarrollo', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    fase = Fase(nombre='Pruebas', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    return None


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.django_db
class TestModeloFase:
    def test_nueva_fase_al_inicio(self, proyecto):
        """
        Prueba unitaria para verificar que el metodo posicionar de una fase modifique correctamente el
        atributo fase_anterior de la fase siguiente en donde se inserta la fase.

        Se espera:
            El aterior de la fase 1 sea la nueva fase que se inserte

        Mensaje de error:
            No se logra posicionar la fase la principio
        """
        fase_2 = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase_2.fase_anterior = None
        fase_2.save()
        fase_1 = Fase(nombre='Disenho', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase_1.fase_anterior = None
        fase_1.save()
        fase_1.posicionar_fase()
        fase_1 = Fase.objects.get(id=fase_1.id)
        fase_2 = Fase.objects.get(id=fase_2.id)
        assert fase_1.fase_anterior is None and fase_2.fase_anterior.pk == fase_1.pk, "No se logra posicionar una fase al inicio"

    def test_nueva_fase_al_final(self, proyecto):
        """
        Prueba unitaria para verificar que el metodo posicionar comprueba que se esta posisionando
        una fase al final.

        Se espera:
            Que la fase que se inserto apunte a la fase que anteriormente era la ultima

        Mensaje de error:
            No se logra posicionar la fase la final
        """
        fase_2 = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase_2.fase_anterior = None
        fase_2.save()
        fase_3 = Fase(nombre='Disenho', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase_3.fase_anterior = fase_2
        fase_3.save()
        fase_3.posicionar_fase()
        fase_2 = Fase.objects.get(id=fase_2.id)
        fase_3 = Fase.objects.get(id=fase_3.id)
        assert fase_2.fase_anterior is None and fase_3.fase_anterior.pk == fase_2.pk, "No se logra posicionar una fase al final"

    def test_nueva_fase_medio(self, proyecto):
        """
        Prueba unitaria para verificar que el metodo posicionar de una fase modifique correctamente el
        atributo fase_anterior de las fases adyacentes de una nueva fase.

        Se espera:
            El aterior de la fase 1 se None
            El de la fase 2 sea la fase 1
            El de la fase 3 sea la fase 2

        Mensaje de error:
            No se logra posicionar una fase entre dos fases
        """

        fase_1 = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase_1.fase_anterior = None
        fase_1.save()
        fase_3 = Fase(nombre='Pruebas', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase_3.fase_anterior = fase_1
        fase_3.save()
        fase_2 = Fase(nombre='Disenho', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase_2.fase_anterior = fase_1
        fase_2.save()
        fase_2.posicionar_fase()
        fase_1 = Fase.objects.get(id=fase_1.id)
        fase_2 = Fase.objects.get(id=fase_2.id)
        fase_3 = Fase.objects.get(id=fase_3.id)
        assert fase_1.fase_anterior is None and fase_2.fase_anterior.pk == fase_1.pk and fase_3.fase_anterior.pk == fase_2.pk, "No se logra posicionar una fase entre dos fases"

    # TODO: Marcelo: test probando get_items de modelo Fase

    # TODO: Luis: test para probar get_item_estado


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.django_db
class TestVistasFase:

    def test_visualizar_fase_view(self, cliente_loggeado, proyecto):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de visualizar fase.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        fase = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase.save()

        response = cliente_loggeado.get(reverse('visualizar_fase', args=(proyecto.id, fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_listar_fase_view(self, cliente_loggeado, proyecto):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de visualizar fase.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        response = cliente_loggeado.get(reverse('listar_fases', args=(proyecto.id, )))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    # TODO: Luis test_nueva_fase_view
    # TODO: Luis test_editar_fase_view
    # TODO: Lios test_eliminar_fase_view
    pass
