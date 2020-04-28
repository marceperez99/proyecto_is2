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


@pytest.mark.django_db
class TestModeloItem:
    """
    Pruebas unitarias que comprueban el funcionamiento del Modelo Item.
    """

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

    @pytest.mark.parametrize('estado_item,esperado', [(EstadoDeItem.NO_APROBADO, EstadoDeItem.A_APROBAR),
                                                      (EstadoDeItem.APROBADO, EstadoDeItem.APROBADO),
                                                      (EstadoDeItem.A_APROBAR, EstadoDeItem.A_APROBAR),
                                                      (EstadoDeItem.EN_LINEA_BASE, EstadoDeItem.EN_LINEA_BASE),
                                                      (EstadoDeItem.ELIMINADO, EstadoDeItem.ELIMINADO),
                                                      (EstadoDeItem.A_MODIFICAR, EstadoDeItem.A_MODIFICAR),
                                                      (EstadoDeItem.EN_REVISION, EstadoDeItem.EN_REVISION), ])
    def test_solicitar_aprobacion_item(self, item, estado_item, esperado):
        """
        Prueba unitaria que verifica funcionamiento del metodo solicitar_aprobacion del modelo Item.

        Se espera:
            - Que el estado del item solo cambie a A_APROBAR si el estado actual del item es NO_APROBADO.

        Mensaje de error:
            - El metodo solicitar_aprobacion() debe dejar el item en estado {esperado} si el item está en estado
            {estado_item}, pero el metodo retornó {item.estado}
        """
        item.estado = estado_item
        try:
            item.solicitar_aprobacion()
        except:
            pass
        assert item.estado == esperado, f'El metodo solicitar_aprobacion debe dejar el item en estado {esperado} ' \
                                        f'si el item está en estado {estado_item}, pero el metodo retornó {item.estado}'

    @pytest.mark.parametrize('estado_item,esperado', [(EstadoDeItem.NO_APROBADO, EstadoDeItem.NO_APROBADO),
                                                      (EstadoDeItem.APROBADO, EstadoDeItem.APROBADO),
                                                      (EstadoDeItem.A_APROBAR, EstadoDeItem.APROBADO),
                                                      (EstadoDeItem.EN_LINEA_BASE, EstadoDeItem.EN_LINEA_BASE),
                                                      (EstadoDeItem.ELIMINADO, EstadoDeItem.ELIMINADO),
                                                      (EstadoDeItem.A_MODIFICAR, EstadoDeItem.A_MODIFICAR),
                                                      (EstadoDeItem.EN_REVISION, EstadoDeItem.EN_REVISION), ])
    def test_aprobar_item_solicitado(self, item, estado_item, esperado):
        """
        Prueba Unitaria que verifica el funcionamineto del metodo aprobar del Modelo Item.

        Se espera:
            - Que el estado del item solo cambie a APROBADO si el estado actual del item es A_APROBADO.

        Mensaje de error:
            - El metodo aprobar() debe dejar el item en estado {esperado} si el item está en estado
            {estado_item}, pero el metodo retornó {item.estado}
        """
        item.estado = estado_item
        try:
            item.aprobar()
        except:
            pass
        assert item.estado == esperado, f'El metodo aprobar() debe dejar el item en estado {esperado} si el item está' \
                                        ' en estado {estado_item}, pero el metodo retornó {item.estado}'

    def test_get_versiones(self, item):
        """
        Prueba Unitaria que verifica que el metodo get_versiones retorne la lista con todas las versiones de un item.

        Se espera:
            - Que el metodo retorne la lista de versiones ordenadas descendentemente.

        Mensaje de Error:
            - La cantidad de versiones retornadas por el metodo y las que realmente estan 'guardadads en el
            sistema no coinciden
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
        condicion = versiones_ordenadas and len(versiones) == len(test_versiones)
        assert condicion is True, 'La cantidad de versiones retornadas por el metodo y las que realmente estan ' \
                                  'guardadads en el sistema no coinciden'

    @pytest.mark.parametrize('estado_item,esperado', [(EstadoDeItem.NO_APROBADO, EstadoDeItem.NO_APROBADO),
                                                      (EstadoDeItem.APROBADO, EstadoDeItem.NO_APROBADO),
                                                      (EstadoDeItem.A_APROBAR, EstadoDeItem.NO_APROBADO),
                                                      (EstadoDeItem.EN_LINEA_BASE, EstadoDeItem.EN_LINEA_BASE),
                                                      (EstadoDeItem.ELIMINADO, EstadoDeItem.ELIMINADO),
                                                      (EstadoDeItem.A_MODIFICAR, EstadoDeItem.A_MODIFICAR),
                                                      (EstadoDeItem.EN_REVISION, EstadoDeItem.EN_REVISION), ])
    def test_desaprobar_item(self, item, estado_item, esperado):
        """
        Prueba Unitaria que comprueba que el estado del item quede en estado No Aprobado.\n
        Se espera:
            Que el item quede en estado No Aprobado, si este se encuentra con los estados Aprobado, A Aprobar y
            No Aprobado. Si se encuentra en otro estado este no cambia\n
        Mensaje de error:
            El metodo desaprobar() debe dejar el item en estado {esperado} si el item está en estado {estado_item},
            pero el metodo retornó {item.estado}
        """
        item.estado = estado_item
        try:
            item.desaprobar()
        except:
            pass
        assert item.estado == esperado, f'El metodo desaprobar() debe dejar el item en estado {esperado} si el item está' \
                                        ' en estado {estado_item}, pero el metodo retornó {item.estado}'


@pytest.mark.django_db
class TestVistasItem:
    """
    Pruebas Unitarias que comprueban el funcionamiento correcto de las vistas referentes a los Items de un Proyecto.
    """

    def test_listar_items_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de listar items.

        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).

        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('listar_items', args=(proyecto.id, item.get_fase().id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_visualizar_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de visualizar un item.

        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).

        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
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

        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).

        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
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

        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).

        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
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

        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).

        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('aprobar_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL. ' \
                                                      'Se esperaba un status code 300.'

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
    # TODO: Luis test_eliminar_relacion_view
