from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_item.models import Item
from gestion_de_proyecto.models import EstadoDeProyecto
from gestion_de_proyecto.tests.factories import proyecto_factory
from gestion_de_tipo_de_item.forms import AtributoCadenaForm, AtributoArchivoForm, AtributoBooleanoForm, \
    AtributoNumericoForm, AtributoFechaForm
from gestion_de_tipo_de_item.tests.factories import tipo_de_item_factory
from gestion_de_tipo_de_item.utils import recolectar_atributos, atributo_form_handler
from roles_de_proyecto.tests.factories import rol_de_proyecto_factory
from roles_de_sistema.tests.factories import rol_de_sistema_factory
from usuario.tests.factories import user_factory


@pytest.fixture
def rs_admin():
    return rol_de_sistema_factory('Admin', 'Descripcion', [p.codename for p in
                                                           Permission.objects.filter(
                                                               content_type__app_label='roles_de_sistema',
                                                               codename__startswith='p')])


@pytest.fixture
def usuario(rs_admin):
    return user_factory('usuario_test', 'password123', 'user@email.com', rs_admin.nombre)


@pytest.fixture
def cliente_loggeado(usuario):
    client = Client()
    client.login(username='usuario_test', password='password123')
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
        'estado': EstadoDeProyecto.CONFIGURACION,
        'fases': [
            {
                'nombre': 'Analisis',
                'descripcion': 'Analisis de Requerimientos'
            }, {
                'nombre': 'Desarrollo',
                'descripcion': 'Desarrollo de Software'
            }, {
                'nombre': 'Pruebas',
                'descripcion': 'Pruebas de Software'
            }
        ],
    })


@pytest.fixture
def tipo_de_item(usuario, proyecto):
    fase = Fase.objects.get(nombre='Analisis')
    return tipo_de_item_factory(fase, {
        'nombre': 'Requerimiento Funcional',
        'descripcion': 'Especificación de un requerimiento funcional.',
        'prefijo': 'RF',
        'creador': usuario.username,
        'fecha_de_creacion': timezone.now(),
        'atributos_dinamicos': [
            {
                'tipo': 'archivo',
                'nombre': 'Diagrama del caso de uso',
                'requerido': False,
                'max_tamaño': 5,
            }, {
                'tipo': 'cadena',
                'nombre': 'Descripcion',
                'requerido': True,
                'max_longitud': 5,
            }, {
                'tipo': 'fecha',
                'nombre': 'Fecha de Cierre',
                'requerido': True,
            }, {
                'tipo': 'numerico',
                'nombre': 'Costo del Caso de Uso',
                'requerido': False,
                'max_digitos': 2,
                'max_decimales': 2
            }, {
                'tipo': 'booleano',
                'nombre': 'Cierto',
                'requerido': True,
            },
        ]
    })


@pytest.fixture
def atributos(tipo_de_item):
    return list(tipo_de_item.atributobinario_set.all()) + list(tipo_de_item.atributobooleano_set.all()) \
           + list(tipo_de_item.atributocadena_set.all()) + list(tipo_de_item.atributofecha_set.all()) + \
           list(tipo_de_item.atributonumerico_set.all())


@pytest.mark.django_db
class TestModeloTipoDeItem:
    """
    Pruebas unitarias que comprueban el funcionamiento de los metodos del Modelo TipoDeItem
    """

    def test_es_utilizado(self, tipo_de_item):
        """
        Prueba unitaria que verifica si algún item es del tipo de item actual.

        Resultado esperado:
            True si algun item es del tipo de item de actual y False si no.

        Mensaje de Error:
            El tipo de item no fue asociado correctamente al item
        """
        item = Item(tipo_de_item=tipo_de_item)
        item.save()
        assert tipo_de_item.es_utilizado(), 'El tipo de item no fue asociado correctamente al item '


@pytest.mark.django_db
class TestUtilsTiposDeItem:
    """
    Pruebas unitarias que comprueban el funcionamiento de las funciones utilitarias de la App.
    """

    def test_recolectar_atributos(self, atributos, tipo_de_item):
        """
        Prueba unitaria que verifica que todos los atributos relacionados a un tipo de item sean recolectados
        y cargados en la lista que retorna la función utilitaria recolectar_atributos()

        Resultado esperado:
            Todos los atributos son devueltos por la función.

        Mensaje de Error:
            La función recolectar_atributos() no consigue todos los atributos del tipo de item.

        """
        lista_atributos = recolectar_atributos(tipo_de_item)
        assert len(lista_atributos) == len(
            atributos), "La función recolectar_atributos no consigue todos los atributos del tipo de item."

    def test_atributo_form_hanldler(self, atributos, tipo_de_item):
        """
        Prueba unitaria que verifica que la función atributo_form_handler construya forms adecuados para cada atributo
        del tipo de item.

        Resultado esperado:
            Una lista con un form adecuado para cada atributo del tipo de item.

        Mensaje de error:
            Los forms construidos no son adecuados para los atributos existentes.
        """
        lista_atributos = recolectar_atributos(tipo_de_item)
        lista_forms = atributo_form_handler(lista_atributos)
        forms_adecuados = True
        for atributo, form in zip(lista_atributos, lista_forms):
            tipo = atributo['tipo']
            forms_adecuados = forms_adecuados and ((tipo == 'cadena' and type(form) == AtributoCadenaForm) or (
                    tipo == 'archivo' and type(form) == AtributoArchivoForm) or (tipo == 'numerico' and type(
                form) == AtributoNumericoForm) or (tipo == 'booleano' and type(form) == AtributoBooleanoForm) or (
                                                           tipo == 'fecha' and type(form) == AtributoFechaForm))

        assert len(lista_atributos) == len(
            lista_forms) and forms_adecuados, "La función atributo_form_handler no construye forms adecuados para los atributos"


@pytest.mark.django_db
class TestVistasTipoDeItem:
    """
    Pruebas unitarias que comprueban el funcionamiento de las vistas referentes a los Tipos de Item de un Proyecto.
    """

    def test_editar_tipo_de_item_view(self, cliente_loggeado, proyecto, tipo_de_item):
        """
        Prueba unitaria que verifica que la vista editar_tipo_de_item_view sea accesible.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """
        response = cliente_loggeado.get(
            reverse('editar_tipo_de_item', args=(proyecto.id, tipo_de_item.fase.id, tipo_de_item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'

    def test_tipo_de_item_view(self, cliente_loggeado, proyecto, tipo_de_item):
        """
        Prueba unitaria que verifica que la vista tipo_de_item_view sea accesible.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """
        response = cliente_loggeado.get(
            reverse('tipo_de_item', args=(proyecto.id, tipo_de_item.fase.id, tipo_de_item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'

    def test_listar_tipo_de_item_view(self, cliente_loggeado, proyecto, tipo_de_item):
        """
        Prueba unitaria que verifica que la vista listar_tipo_de_item_view sea accesible.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """
        response = cliente_loggeado.get(
            reverse('tipos_de_item', args=(proyecto.id, tipo_de_item.fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'

    def test_nuevo_tipo_de_item_view(self, cliente_loggeado, proyecto, tipo_de_item):
        """
        Prueba unitaria que verifica que la vista nuevo_tipo_de_item_view sea accesible.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """
        response = cliente_loggeado.get(
            reverse('nuevo_tipo_de_item', args=(proyecto.id, tipo_de_item.fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'

    def test_importar_tipo_de_item_view(self, cliente_loggeado, proyecto, tipo_de_item):
        """
        Prueba unitaria que verifica que la vista importar_tipo_de_item_view sea accesible.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """
        response = cliente_loggeado.get(
            reverse('importar_tipo_de_item', args=(proyecto.id, tipo_de_item.fase.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'

    def test_nuevo_tipo_de_item_importar_view(self, cliente_loggeado, proyecto, tipo_de_item):
        """
        Prueba unitaria que verifica que la vista nueo_tipo_de_item_view con el \
        argumento opcional tipo_de_item sea accesible.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL
        """
        response = cliente_loggeado.get(
            reverse('nuevo_tipo_de_item_importar', args=(proyecto.id, tipo_de_item.fase.id, tipo_de_item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'

    def test_eliminar_tipo_de_item_view(self, cliente_loggeado, proyecto, tipo_de_item):
        """
        Prueba unitaria que verifica que la vista eliminar_tipo_de_item_view con el \
        argumento opcional tipo_de_item sea accesible.

        Resultado Esperado:
            -Una respuesta HTTP con codigo 200.

        Mensaje de Error:
            -Hubo un error al tratar de acceder a la URL.
        """
        response = cliente_loggeado.get(
            reverse('nuevo_tipo_de_item_importar', args=(proyecto.id, tipo_de_item.fase.id, tipo_de_item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL.'
