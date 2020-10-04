from http import HTTPStatus
import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from gestion_de_fase.models import Fase
from gestion_de_fase.utils import puede_cerrar_fase
from gestion_de_fase.tests.factories import fase_factory
from gestion_de_item.models import Item, VersionItem, EstadoDeItem
from gestion_de_item.tests.factories import item_factory
from gestion_de_proyecto.models import EstadoDeProyecto
from gestion_de_proyecto.tests.factories import proyecto_factory
from gestion_de_tipo_de_item.tests.factories import tipo_de_item_factory
from roles_de_proyecto.tests.factories import rol_de_proyecto_factory
from roles_de_sistema.tests.factories import rol_de_sistema_factory
from usuario.tests.factories import user_factory
import gestion_de_fase.tests.test_case as tc


@pytest.fixture
def rs_admin():
    return rol_de_sistema_factory('Admin', 'Administrador del Sistema',
                                  [p.codename for p in
                                   Permission.objects.filter(content_type__app_label='roles_de_sistema',
                                                             codename__startswith='p')])


@pytest.fixture
def usuario(rs_admin):
    return user_factory('user_test', 'password123', 'test@admin.com', rs_admin.nombre)


@pytest.fixture
def cliente_loggeado(usuario):
    client = Client()
    client.login(username='user_test', password='password123')
    return client


@pytest.fixture
def rol_de_proyecto():
    return rol_de_proyecto_factory({
        'nombre': 'Desarrollador',
        'descripcion': 'Descripcion del Rol',
        'permisos': [p.codename for p in Permission.objects.all().filter(codename__startswith='pp_')]
    })


@pytest.fixture
def proyecto(usuario):
    return proyecto_factory({
        'nombre': 'Proyecto de Prueba',
        'descripcion': 'Descripcion de Prueba',
        'creador': usuario.username,
        'gerente': usuario.username,
        'estado': EstadoDeProyecto.CONFIGURACION
    })


@pytest.fixture()
def fase(proyecto):
    return fase_factory(proyecto, None, {'nombre': 'Analisis', 'descripcion': 'Descripcion de Fase'})


@pytest.fixture
def tipo_de_item(fase, usuario):
    return tipo_de_item_factory(fase, {
        'nombre': 'Requerimiento Funcional', 'creador': usuario.username, 'fase': fase, 'prefijo': "RF",
        'descripcion': 'Especificacion de requerimiento funcional', 'fecha_de_creacion': timezone.now()
    })


@pytest.fixture
def item(tipo_de_item):
    return item_factory({
        'tipo': 'Requerimiento Funcional',
        'estado': EstadoDeItem.NO_APROBADO,
        'codigo': 'RF_1',
        'estado_anterior': '',
        'version': 1,
        'versiones': {
            1: {
                'nombre': 'Nombre de item',
                'descripcion': 'Descripcion',
                'peso': 5,
            }
        }

    })


@pytest.mark.django_db
class TestModeloFase:
    """
    Pruebas unitarias que comprueban el funcionamiento de los métodos del Modelo Fase.
    """

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

    def test_get_items(self, fase, tipo_de_item, item):
        """
        Prueba Unitaria que comprueba que el metodo get_items retorne todos los items que no estén eliminados
        dentro una fase.

        Se espera:
            Que se retornen todos los items de la fase del proyecto.
        Mensaje de error:
            El metodo get_items no retorna correctamente los items de una fase.
        """
        new_item = Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.ELIMINADO, codigo="")
        version = VersionItem.objects.create(item=new_item, descripcion="Descripcion del item", version=1,
                                             nombre="Item",
                                             peso=1)
        new_item.version = version
        new_item.save()

        assert len(fase.get_items()) == len([item]), "El metodo get_items no retorna correctamente " \
                                                     "los items de una fase."

    def test_get_items_eliminados(self, fase, tipo_de_item, item):
        """
        Prueba Unitaria que comprueba que el metodo get_items retorne todos los items de una fase, incluso
        aquellos items ya eliminados.

        Se espera:
            Que se retornen todos los items de la fase del proyecto.
        Mensaje de error:
            El metodo get_items no retorna correctamente los items de una fase.
        """
        new_item = Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.ELIMINADO, codigo="")
        version = VersionItem.objects.create(item=new_item, descripcion="Descripcion del item", version=1,
                                             nombre="Item",
                                             peso=1)
        new_item.version = version
        new_item.save()
        condicion = len(fase.get_items(items_eliminados=True)) == len([item, new_item])
        assert condicion is True, "El metodo get_items no retorna correctamente los items de una fase."

    def test_get_items_vacio(self, fase):
        """
        Prueba Unitaria que comprueba que el metodo get_items no retorne ningun item .

        Se espera:
            Que se retornen todos los items de la fase del proyecto.
        Mensaje de error:
            El metodo get_items no retorna correctamente los items de una fase.

        """
        assert fase.get_items() == [], "El metodo get_items no retorna correctamente " \
                                       "los items de una fase."

    def test_get_item_estado_un_estado(self, fase, tipo_de_item):
        """
        Prueba Unitaria que comprueba que el metodo get_item_estado retorne los item con el estados
        especificados en los parametros de la funcion.

        Se espera:
            Que se retornen todos los items de la fase que tengan el estado especificado
        Mensaje de error:
            El metodo get_item_estado no retorna correctamente los items de una fase.

        """
        items = [Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.NO_APROBADO, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.APROBADO, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.APROBADO, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.EN_LINEA_BASE, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo="")]
        list_item = list(fase.get_item_estado(EstadoDeItem.A_APROBAR))
        list_a_aprobar = list(filter(lambda e: e.estado == EstadoDeItem.A_APROBAR, items))
        condicion = all(item in list_item for item in list_a_aprobar) and all(
            item in list_a_aprobar for item in list_item)
        assert condicion is True, f'El metodo get_item_estado no retorna correctamente los items de una fase'

    def test_get_item_estado_varios_estados(self, fase, tipo_de_item):
        """
        Prueba Unitaria que comprueba que el metodo get_item_estado retorne los item con los estados
        especificados en los parametros de la funcion.

        Se espera:
            Que se retornen todos los items de la fase que tengan los estados especificados
        Mensaje de error:
            El metodo get_item_estado no retorna correctamente los items de una fase.

        """
        items = [Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.NO_APROBADO, codigo="TT_6"),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo="TT_5"),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.APROBADO, codigo="TT_0"),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.APROBADO, codigo="TT_1"),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.EN_LINEA_BASE, codigo="TT_2"),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo="TT_3"),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.EN_LINEA_BASE, codigo="TT_4")]
        list_item = list(fase.get_item_estado(EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE))
        list_estados = list(
            filter(lambda e: e.estado == EstadoDeItem.APROBADO or e.estado == EstadoDeItem.EN_LINEA_BASE, items))
        condicion = all(item in list_item for item in list_estados) and all(item in list_estados for item in list_item)
        assert condicion is True, f'El metodo get_item_estado no retorna correctamente los items de una fase'

    def test_get_item_estado_ninguno(self, fase, tipo_de_item):
        """
        Prueba Unitaria que comprueba que el metodo get_item_estado retorne un objeto null, al no encontrar ningun item
        con el estado especificado.

        Se espera:
            Que se retornen null
        Mensaje de error:
            El metodo get_item_estado no retorna lo esperado.

        """
        items = [Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.NO_APROBADO, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.APROBADO, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.APROBADO, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.EN_LINEA_BASE, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo=""),
                 Item.objects.create(tipo_de_item=tipo_de_item, estado=EstadoDeItem.A_APROBAR, codigo="")]
        list_item = list(fase.get_item_estado(EstadoDeItem.ELIMINADO))
        list_null = list(filter(lambda e: e.estado == EstadoDeItem.ELIMINADO, items))
        condicion = all(item in list_item for item in list_null) and all(item in list_null for item in list_item)
        assert condicion is True, f'El metodo get_item_estado no retorna lo esperado.'


    @pytest.mark.parametrize('fase,resultado_esperado', tc.test_cerrar_fase_result.items())
    def test_cerrar_fase(self, rol_de_proyecto, rs_admin, fase, resultado_esperado):
        """
        TODO Luis, cargar en planilla
        Prueba unitaria encargada de probar el funcionamiento del metodo cerrar de la clase Fase,
        encargada de verificar si una fase del proyecto puede ser cerrada.

        Resultado Esperado:
            -Que el atributo de la Fase fase_cerrada cambie su valor a True

        Mensajes de Error:
            -La fase anterior {self.fase_anterior.nombre} todavia esta sin cerrar, si la fase anterior no esta cerrada
            -El item {item.version.nombre} no esta en una Linea Base, si el item no esta en una linea base
            -El item {item.version.nombre} no es trazable a la siguiente fase, si el item no tiene sucesores
        """
        rol_de_proyecto_factory(tc.rol_de_proyecto)
        user_factory(tc.user['username'], tc.user['password'], tc.user['email'], rs_admin.nombre)
        user_factory(tc.user2['username'], tc.user2['password'], tc.user2['email'], rs_admin.nombre)
        user_factory(tc.gerente['username'], tc.gerente['password'], tc.gerente['email'], rs_admin.nombre)
        proyecto = proyecto_factory(tc.proyecto)
        fase = Fase.objects.get(nombre=fase)
        with pytest.raises(Exception) as excinfo:
            fase.cerrar()
        condicion = all(mensaje in resultado_esperado for mensaje in list(excinfo.value.args)[0])
        assert condicion, f'El metodo no lanza las exceptiones corresponientes, se espera los siguientes mensajes: \n' \
                          f'{resultado_esperado}'


    @pytest.mark.parametrize('fase,resultado_esperado', tc.test_es_ultima_fase_result.items())
    def test_es_ultima_fase(self, rol_de_proyecto, rs_admin, fase, resultado_esperado):
        """
        #TODO Luis, cargar en planilla
        Prueba unitaria encargada de probar el funcionamiento del metodo es_ultima_fase, de la clase Fase,
        encargada de verificar si la fase del proyecto es la ultima.

        Resultado Esperado:
            -Que retorne verdadero si la fase es la ultima del proyecto

        Mensajes de Error:
            -'El metodo lanza una respuesta incorrecta, se esperaba un {resultado_esperado}, pero devuelve un {condicion}
        """
        rol_de_proyecto_factory(tc.rol_de_proyecto)
        user_factory(tc.user['username'], tc.user['password'], tc.user['email'], rs_admin.nombre)
        user_factory(tc.user2['username'], tc.user2['password'], tc.user2['email'], rs_admin.nombre)
        user_factory(tc.gerente['username'], tc.gerente['password'], tc.gerente['email'], rs_admin.nombre)
        proyecto = proyecto_factory(tc.proyecto)
        fase = Fase.objects.get(nombre=fase)
        condicion = fase.es_ultima_fase()
        assert condicion == resultado_esperado, f'El metodo lanza una respuesta incorrecta, se esperaba un {resultado_esperado}' \
                                                f' pero devuelve un {condicion}'

@pytest.mark.django_db
class TestVistasFase:
    """
    Pruebas unitarias que comprueban el funcionamiento de las vistas referentes a las Fases de un Proyecto.
    """

    @pytest.mark.parametrize('estado_proyecto', [(EstadoDeProyecto.CONFIGURACION),
                                                 (EstadoDeProyecto.INICIADO)])
    def test_visualizar_fase_view(self, cliente_loggeado, proyecto, estado_proyecto):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de visualizar fase.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        proyecto.estado = estado_proyecto
        proyecto.save()
        fase = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False)
        fase.save()
        response = cliente_loggeado.get(reverse('visualizar_fase', args=(proyecto.id, fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    @pytest.mark.parametrize('estado_proyecto', [(EstadoDeProyecto.CONFIGURACION),
                                                 (EstadoDeProyecto.INICIADO)])
    def test_listar_fase_view(self, cliente_loggeado, proyecto, estado_proyecto):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de visualizar fase.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        proyecto.estado = estado_proyecto
        proyecto.save()
        response = cliente_loggeado.get(reverse('listar_fases', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_nueva_fase_view(self, cliente_loggeado, proyecto):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de nueva fase.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        proyecto.estado = EstadoDeProyecto.CONFIGURACION
        proyecto.save()
        response = cliente_loggeado.get(reverse('nueva_fase', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_editar_fase_view(self, cliente_loggeado, proyecto, fase):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de editar fase.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        proyecto.estado = EstadoDeProyecto.CONFIGURACION
        proyecto.save()
        response = cliente_loggeado.get(reverse('editar_fase', args=(proyecto.id, fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_eliminar_fase_view(self, cliente_loggeado, proyecto, fase):
        """
            Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
            vista de eliminar fase.

            Se espera:
                Que la respuesta HTTP sea OK.

            Mensaje de Error:
                Hubo un error al tratar de acceder a la URL
            """
        proyecto.estado = EstadoDeProyecto.CONFIGURACION
        proyecto.save()
        response = cliente_loggeado.get(reverse('eliminar_fase', args=(proyecto.id, fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_cerrar_fase_view(self, cliente_loggeado, proyecto, fase):
        """
        #TODO Luis, cargar en planilla
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de cerrar fase.

        Se espera:
            -Que la respuesta HTTP sea OK.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('cerrar_fase', args=(proyecto.id, fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'


