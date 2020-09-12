import datetime
from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_item.tests.factories import item_factory
from gestion_de_proyecto.models import Proyecto, Participante, EstadoDeProyecto
from gestion_de_proyecto.tests.factories import participante_factory
from gestion_de_tipo_de_item.models import TipoDeItem
from gestion_de_tipo_de_item.tests.factories import tipo_de_item_factory
from roles_de_proyecto.tests.factories import rol_de_proyecto_factory
from gestion_de_item.models import VersionItem, EstadoDeItem
from roles_de_sistema.tests.factories import rol_de_sistema_factory
from usuario.tests.factories import user_factory


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
        'descripcion': 'Descripcion de rol',
        'permisos': [p.codename for p in Permission.objects.all().filter(codename__startswith='pp_')]
    })


@pytest.fixture
def proyecto(usuario, rol_de_proyecto):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba',
                        fecha_de_creacion=datetime.datetime.now(tz=timezone.utc),
                        creador=usuario, gerente=usuario)
    proyecto.save()
    fase1 = Fase(nombre='Analisis', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False, fase_anterior=None)
    fase1.save()
    fase2 = Fase(nombre='Desarrollo', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False, fase_anterior=fase1)
    fase2.save()
    fase3 = Fase(nombre='Pruebas', proyecto=proyecto, fase_cerrada=False, puede_cerrarse=False, fase_anterior=fase2)
    fase3.save()
    participante = Participante.objects.create(proyecto=proyecto, usuario=usuario)
    participante.save()
    return proyecto


@pytest.fixture
def usuario_participante(rs_admin):
    return user_factory('user_test_1', 'passrowe123', 'test1@admin.com', rs_admin.nombre)


@pytest.fixture
def participante(proyecto, usuario_participante, rol_de_proyecto):
    participante = Participante.objects.create(proyecto=proyecto, usuario=usuario_participante)
    participante.asignar_rol_de_proyecto(rol_de_proyecto)
    participante.save()
    return participante


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


@pytest.fixture()
def tipo_de_item_fase2(usuario, proyecto):
    fase = Fase.objects.get(nombre="Desarrollo")
    return tipo_de_item_factory(fase, {'nombre': "Requerimiento NO Funcional",
                                       'descripcion': "Especificacion de un requerimiento NO funcional",
                                       'prefijo': "RT",
                                       'creador': usuario,
                                       'fecha_de_creacion': timezone.now(),
                                       })


@pytest.fixture
def item(tipo_de_item):
    return item_factory({
        'tipo': 'Requerimiento Funcional',
        'estado': EstadoDeItem.NO_APROBADO,
        'codigo': 'RF_1',
        'estado_anterior': '',
        'version': 2,
        'versiones': {
            1: {
                'nombre': 'Nombre de item',
                'descripcion': 'Descripcion',
                'peso': 5,
            },
            2: {
                'nombre': 'Nombre de item 2',
                'descripcion': 'Descripcion 2',
                'peso': 6,
            }
        }

    })


@pytest.fixture
def item2(tipo_de_item_fase2, item):
    return item_factory({
        'tipo': 'Requerimiento NO Funcional',
        'estado': EstadoDeItem.NO_APROBADO,
        'codigo': 'RT_1',
        'estado_anterior': '',
        'version': 2,
        'versiones': {
            1: {
                'nombre': 'Nombre de item',
                'descripcion': 'Descripcion',
                'peso': 8,
                'antecesores': ['RF_1'],
            },
            2: {
                'nombre': 'Nombre 2',
                'descripcion': 'Descripcion 2',
                'peso': 6,
            }
        }

    })


@pytest.fixture
def item_a_modificar(item, participante):
    item.encargado_de_modificar = participante
    item.estado = EstadoDeItem.A_MODIFICAR
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
        assert item.version.version == 3, 'No fue creada una nueva versión'

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
            - El metodo solicitar_aprobacion() debe dejar el item en estado {esperado} si \
            el item está en estado {estado_item}, pero el metodo retornó {item.estado}
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
                                                      (EstadoDeItem.A_MODIFICAR, EstadoDeItem.APROBADO),
                                                      (EstadoDeItem.EN_REVISION, EstadoDeItem.EN_REVISION), ])
    def test_aprobar_item_solicitado(self, item, estado_item, esperado):
        """
        Prueba Unitaria que verifica el funcionamineto del metodo aprobar del Modelo Item.

        Se espera:

            - Que el estado del item solo cambie a APROBADO si el estado actual del item es A_APROBADO.

        Mensaje de error:
            - El metodo aprobar() debe dejar el item en estado {esperado} si el item está en estado {estado_item},
                pero el metodo retornó {item.estado}.\n
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
            - La cantidad de versiones retornadas por el metodo y las que realmente estan 'guardadads en el sistema no coinciden.

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

    def test_solicitar_modificacion_item_a_usuario(self, item, participante):
        """
        Prueba Unitaria que comprueba que el al indicar que un item debe ser modificado este pase al estado A Modificar
        y se asigne correctamente el usuario que debe modificar el item.\n
        Se espera:
            Que el item quede en estado A Modificar, el campo encargado_de_modificar del item quede con el
            participante indicado\n
        Mensaje de error:
            El estado del item debe ser {EstadoDeItem.A_MODIFICAR} pero el item esta en estado {item.estado}
            y el encargado_de_modificar deberia ser {participante} pero es {item.encargado_de_modificar}
        """
        # TODO incluir en archivo de documentacion
        item.solicitar_modificacion(participante)

        condicion = item.estado == EstadoDeItem.A_MODIFICAR and item.encargado_de_modificar == participante
        assert condicion, f'El estado del item debe ser {EstadoDeItem.A_MODIFICAR} pero el item esta en estado {item.estado} ' \
                          f'y el encargado_de_modificar deberia ser {participante} pero es {item.encargado_de_modificar}'

    def test_solicitar_revision(self, item):
        """
        Prueba Unitaria que el metodo solicitar_revision\n
        Se espera:
            Que el item quede en estado A Modificar, el campo encargado_de_modificar del item quede con el
            participante indicado\n
        Mensaje de error:
            El estado del item debe ser "En Revision" pero esta en estado {item.estado}
            y el estado_anterior deberia ser Aprobado pero es {item.estado_anterior}
        """
        # TODO incluir en archivo de documentacion
        item.estado = EstadoDeItem.APROBADO
        item.solicitar_revision()

        condicion = item.estado == EstadoDeItem.EN_REVISION and item.estado_anterior == EstadoDeItem.APROBADO
        assert condicion, f'El estado del item debe ser "En Revision" pero esta en estado {item.estado} ' \
                          f'y el estado_anterior deberia ser Aprobado pero es {item.estado_anterior}'

    def test_puede_modificar_item_a_modificar(self, item_a_modificar, participante):
        """
        TODO: Marcelo incluir en la planilla
        Prueba unitaria que comprueba que el metodo puede_modificar del modelo Item retorna \
        correctamente que un participante asignado para modificar un item puede modificar el item.

        Se espera:
            - Que el metodo retorne True.

        Mensaje de Error:
            - El item deberia ser modificable por el usuario.
        """
        assert item_a_modificar.puede_modificar(participante), f'El item deberia ser modificable por el usuario'

    def test_puede_modificar_item_a_modificar_sin_encargado(self, rs_admin, rol_de_proyecto, proyecto,
                                                            item_a_modificar):
        """
        TODO: Marcelo cargar en la planilla
        Prueba unitaria que comprueba que el metodo puede_modificar del modelo Item retorna \
        correctamente que un participante pueda modificar un item que ha sido puesto para ser modificado \
        por cualquier usuario con el permiso correspondiente.

        Se espera:
            - Que el metodo retorne True.

        Mensaje de Error:
            - El item deberia ser modificable por el usuario.
        """
        item_a_modificar.encargado_de_modificar = None
        user = user_factory('user_test_2', 'password123', 'test2@admin.com', rs_admin.nombre)
        participante = participante_factory(proyecto, {
            'usuario': user.username,
            'rol_de_proyecto': rol_de_proyecto.nombre,
            'permisos': {
                'Analisis': ['pp_f_modificar_item', 'pu_f_ver_fase'],
                'Desarrollo': [],
                'Pruebas': []
            }
        })
        assert item_a_modificar.puede_modificar(participante), f'El item deberia ser modificable por el usuario'

    def test_no_puede_modificar_item_a_modificar(self, rs_admin, rol_de_proyecto, proyecto, item_a_modificar):
        """
        TODO: Marcelo cargar en la planilla
        Prueba unitaria que comprueba que el metodo puede_modificar del modelo Item retorna \
        correctamente que un participante, que no fue asignado para modificar un item, no puede el item.

        Se espera:
            - Que el metodo retorne False.

        Mensaje de Error:
            - El item no debe ser modificable por otro usuario que no sea el asignado
        """
        user = user_factory('user_test_3', 'passrowe123', 'test3@admin.com', rs_admin.nombre)
        participante = participante_factory(proyecto, {
            'usuario': user.username,
            'rol_de_proyecto': rol_de_proyecto.nombre,
            'permisos': {
                'Analisis': ['pu_f_ver_fase'],
                'Desarrollo': [],
                'Pruebas': []
            }
        })
        assert not item_a_modificar.puede_modificar(participante), 'El item no debe ser modificable por otro ' \
                                                                   'usuario que no sea el asignado'

    def test_puede_restaurarse_estado(self, item):
        #TODO subir en la planilla de funciones
        """
        Prueba Unitaria para el metodo puede_restaurarse item\n
        Se espera:
            Que el metodo de como resultado Falso, esto indica que el item no se encuntra en estado No Aprobado\n
        Mensaje de error:
            'El item no se puede restaurar a la version {item.version.version}, pues el item no esta con estado No Aprobado'
        """
        item.estado = EstadoDeItem.APROBADO
        item.save()
        version = item.get_versiones()[1]
        condicion = item.puede_restaurarse(version)
        assert condicion == False, f'El item no se puede restaurar a la version {item.version.version},' \
                                   f'pues el item no esta con estado No Aprobado'

    def test_puede_restaurarse_fase(self, item):
        # TODO subir en la planilla de funciones
        """
        Prueba Unitaria para el metodo puede_restaurarse item\n
        Se espera:
            Que el metodo de como resultado Verdadero, esto indica que el item se encuentra en la primera fase\n
        Mensaje de error:
            'El item no se puede restaurar a la version {item.version.version}, pues el item no esta en la primera fase'
        """
        version = item.get_versiones()[1]
        condicion = item.puede_restaurarse(version)
        assert condicion == True, f'El item no se puede restaurar a la version {item.version.version}, ' \
                                  f'pues el item no esta en la primera fase'

    def test_puede_restaurarse_antecesores(self, item, item2):
        # TODO subir en la planilla de funciones
        """
        Prueba Unitaria para el metodo puede_restaurarse item\n
        Se espera:
            Que el metodo de como resultado Verdadero, esto indica que el item tiene al menos un antecesor en la version
            a la cual quiere volver, por lo que puede ser restaurado\n
        Mensaje de error:
            'El item no se puede restaurar a la version {item.version.version}, pues en esta no es trazable a la primera fase'
        """
        item.estado = EstadoDeItem.EN_LINEA_BASE
        item.save()
        version = item2.get_versiones()[1]
        condicion = item2.puede_restaurarse(version)
        assert condicion == True, f'El item no se puede restaurar a la version {item2.version.version}, ' \
                                  f'pues en esta no trazabe a la primera fase'

    def test_puede_restaurarse_padres(self, item, item2, tipo_de_item_fase2):
        # TODO subir en la planilla de funciones
        """
        Prueba Unitaria para el metodo puede_restaurarse item\n
        Se espera:
            Que el metodo de como resultado Falso, esto indica que el item tiene al menos un padre en la version
            a la cual quiere volver, por lo que puede ser restaurado\n
        Mensaje de error:
            'El item no se puede restaurar a la version {item.version.version}, pues en esta no es trazable a la primera fase'
        """
        item2.estado = EstadoDeItem.APROBADO
        item2.save()
        item3 = item_factory({
            'tipo': 'Requerimiento NO Funcional',
            'estado': EstadoDeItem.NO_APROBADO,
            'codigo': 'RT_2',
            'estado_anterior': '',
            'version': 2,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 8,
                    'padres': ['RT_1']
                },
                2: {
                    'nombre': 'Nombre 2',
                    'descripcion': 'Descripcion 2',
                    'peso': 6,
                }
            }

        })
        item.estado = EstadoDeItem.APROBADO
        item.save()
        version = item3.get_versiones()[1]
        condicion = item3.puede_restaurarse(version)
        assert condicion == True, f'El item no se puede restaurar a la version {item3.version.version}, ' \
                                  f'pues en esta no es trazable a la primera fase'

    def test_restaurar(self, item):
        # TODO subir en la planilla de funciones
        """
        Prueba Unitaria para el metodo restaurar item\n
        Se espera:
            Que el metodo revierta los cambios el item a una version anterior, esto indica que el item tiene al menos un padre en la version
            a la cual quiere volver, por lo que puede ser restaurado\n
        Mensaje de error:
            'El item no se puede restaurar a la version {item.version.version}, pues en esta no es trazable a la primera fase'
        """
        version = item.get_versiones()[1]
        item.restaurar(version)
        assert item.version.nombre == version.nombre, 'No se pudo restaurar el nombre de esta version'
        assert item.version.descripcion == version.descripcion, 'No se pudo restaurar la descripcion de esta version'
        assert item.version.peso == version.peso, 'No se pudo restaurar el peso de esta version'
        assert item.version.version == item.version_item.all().count(), 'El numero de la version no aumento en 1 con respecto a la ultima'

    def test_restaurar_relaciones(self, item, item2, tipo_de_item, tipo_de_item_fase2):
        # TODO subir en la planilla de funciones
        """

        """
        item.estado = EstadoDeItem.EN_LINEA_BASE
        item.save()
        item2.estado = EstadoDeItem.APROBADO
        item4 = item_factory({
            'tipo': 'Requerimiento Funcional',
            'estado': EstadoDeItem.EN_LINEA_BASE,
            'codigo': 'RF_2',
            'estado_anterior': '',
            'version': 1,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 8,
                }
            },
        })
        item5 = item_factory({
            'tipo': 'Requerimiento NO Funcional',
            'estado': EstadoDeItem.APROBADO,
            'codigo': 'RT_3',
            'estado_anterior': '',
            'version': 2,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 8,
                    }
            },
        })
        item3 = item_factory({
            'tipo': 'Requerimiento NO Funcional',
            'estado': EstadoDeItem.NO_APROBADO,
            'codigo': 'RT_2',
            'estado_anterior': '',
            'version': 2,
            'versiones': {
                1: {
                    'nombre': 'Nombre de item',
                    'descripcion': 'Descripcion',
                    'peso': 8,
                    'padres': ['RT_1'],
                    'antecesores': ['RF_1']
                },
                2: {
                    'nombre': 'Nombre 2',
                    'descripcion': 'Descripcion 2',
                    'peso': 6,
                    'padres': ['RT_1', 'RT_3'],
                    'antecesores': ['RF_1', 'RF_2']
                }
            },
        })
        version = item3.get_versiones()[1]
        item3.restaurar(version)
        assert item3.version.nombre == version.nombre, 'No se pudo restaurar el nombre de esta version'
        assert item3.version.descripcion == version.descripcion, 'No se pudo restaurar la descripcion de esta version'
        assert item3.version.peso == version.peso, 'No se pudo restaurar el peso de esta version'
        assert item3.version.version == item3.version_item.all().count(), 'El numero de la version no aumento en 1 con respecto a la ultima'
        assert item3.version.padres.count() == 0, 'No se puede restaurar a la version anterior'
        assert item3.version.antecesores.count() == version.antecesores.count(), f'No se restauro correctamente ' \
                                                                                 f'a la version {item3.version.version}'

    # TODO Luis falta pruebas unitaria de: add_padre
    # TODO Luis falta pruebas unitaria de: add_antecesor
    # TODO Luis falta pruebas unitaria de: eliminar_relacion
    # TODO Hugo test_eliminar_item


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

    def test_solicitar_aprobacion_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de \
        visualizar el historial de cambios de un item.

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
        item.estado = EstadoDeItem.A_APROBAR
        item.save()
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

    def test_desaprobar_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de desaprobar item.\n
        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).\n
        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        item.estado = EstadoDeItem.APROBADO
        item.save()
        proyecto.save()
        response = cliente_loggeado.get(reverse('desaprobar_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL. ' \
                                                      'Se esperaba un status code 300.'

    def test_relacionar_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de relacionar item.\n
        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).\n
        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('relacionar_item', args=(proyecto.id, item.get_fase().id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL. ' \
                                                      'Se esperaba un status code 300.'

    def test_eliminar_relacion_item_view(self, cliente_loggeado, proyecto, item):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de eliminar relacion.\n
        Se espera:
            - Status code de la respuesta del servidor HTTPStatus.OK (300).\n
        Mensaje de Error:
            - No se obtuvo la pagina correctamente. Se esperaba un status code 300.
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = cliente_loggeado.get(reverse('eliminar_relacion_item', args=(proyecto.id, item.get_fase().id,
                                                                                item.id, item.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL. ' \
                                                      'Se esperaba un status code 300.'

    # TODO Hugo: test_debe_modificar_view
    # TODO Luis: test_restaurar_version_item_view