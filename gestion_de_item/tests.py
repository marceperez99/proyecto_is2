import datetime
from http import HTTPStatus
import pytest
from django.contrib.auth.models import User, Permission, Group
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante, EstadoDeProyecto
from gestion_de_tipo_de_item.models import TipoDeItem
from roles_de_proyecto.models import RolDeProyecto
from roles_de_sistema.models import RolDeSistema
from .models import Item, VersionItem, EstadoDeItem


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
def proyecto(usuario, rol_de_proyecto):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba',
                        fecha_de_creacion=datetime.datetime.now(tz=timezone.utc),
                        creador=usuario, gerente=usuario)
    proyecto.save()
    fase = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    fase = Fase(nombre='Desarrollo', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    fase = Fase(nombre='Pruebas', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
    fase.save()
    participante = Participante.objects.create(proyecto=proyecto, usuario=usuario)
    participante.save()
    return proyecto


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
def item(tipo_de_item):
    item = Item(tipo_de_item=tipo_de_item)
    item.estado = EstadoDeItem.NO_APROBADO
    item.save()
    version = VersionItem()
    version.item = item
    version.descripcion = ""
    version.nombre = ""
    version.peso = 2
    version.save()
    item.version = version
    item.save()
    return item


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
@pytest.mark.django_db
class TestModelosItem:

    def test_nueva_version(self, item):
        """
        Prueba unitaria que se encarga de verificar que el metodo nueva_version de un Item genere una nueva versiom

        Resultado Esperado:
            -El numero de versiones aumenta en uno.

        Mensaje de Error:
            -No fue creada una nueva versión.
        """
        item.nueva_version()
        assert item.version.version == 2, 'No fue creada una nueva versión'

    @pytest.mark.django_db
    def test_solicitar_aprobacion_item(self, item):
        """
        Prueba unitaria que verifica que al llamar al metodo solicitar_aprobacion se cambie el estado del
        item a A_Aprobar
        """
        item.solicitar_aprobacion()
        assert item.estado == EstadoDeItem.A_APROBAR, 'El estado del item no cambio a A Aprobar'

    @pytest.mark.django_db
    def test_aprobar_item_solicitado(self, item):
        """
        Prueba Unitaria que verifica que al aprobar un item se cambie el estado del item a Aprobado.
        """
        item.solicitar_aprobacion()
        item.aprobar()
        assert item.estado == EstadoDeItem.APROBADO, 'El estado del item no cambio a A Aprobar'

    @pytest.mark.django_db
    def test_get_versiones(self, item):
        """
        Prueba Unitaria que verifica que el metodo get_versiones retorne la lista con todas las versiones de un item.
        """
        item.nueva_version()
        item.nueva_version()
        versiones = VersionItem.objects.filter(item=item)

        test_versiones = list(item.get_versiones())

        versiones_ordenadas = True
        nro_version = test_versiones[0].version
        # Se verifica que las versiones esten en orden
        for i in range(1, len(test_versiones)):
            if test_versiones[i].version >= nro_version:
                versiones_ordenadas = False
            nro_version = test_versiones[i].version

        assert versiones_ordenadas and len(versiones) == len(test_versiones), 'La cantidad de versiones retornadas ' \
                                                                              'por el metodo y las que realmente estan ' \
                                                                              'guardadads en el sistema no coinciden'

    def test_desaprobar_item(self, item):
        """
        Prueba Unitaria que comprueba que el estado del item quede en estado No Aprobado.
        """
        item.estado = EstadoDeItem.APROBADO
        item.desaprobar()
        assert item.estado == EstadoDeItem.NO_APROBADO, 'El estado del item no cambio a No aprobado'

    pass


@pytest.mark.django_db
class TestVistasItem:

    def test_listar_items_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de listar items.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('listar_items', args=(proyecto.id, item.get_fase().id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_visualizar_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de visualizar un item.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('visualizar_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_nuevo_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de crear un nuevo item.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('nuevo_item', args=(proyecto.id, item.get_fase().id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_eliminar_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de eliminar un item.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('eliminar_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_ver_historial_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de visualizar el historial de cambios
         de un item.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('historial_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    # TODO: Luis test_relacionar_item_view

    def test_solicitar_aprobacion_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de visualizar el historial de cambios
         de un item.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(
            reverse('solicitar_aprobacion_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_aprobar_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de visualizar el historial de cambios
         de un item.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('aprobar_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_editar_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de eliminar un item.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('editar_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'
    # TODO: Luis test_desaprobar_item_view

    # TODO: test_eliminar_relacion_view
