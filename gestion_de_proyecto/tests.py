from http import HTTPStatus
import pytest
from django.contrib.auth.models import User, Permission, Group
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante, EstadoDeProyecto, Comite
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
def usuario():
    user = User(username='usuario_test', email='usuario@gmail.com')
    user.set_password('password123')
    user.save()
    return user


@pytest.fixture
def gerente(rs_admin):
    user = User(username='gerente', email='gerente@gmail.com')
    user.set_password('password123')
    user.save()
    user.groups.add(Group.objects.get(name=rs_admin.nombre))
    return user


@pytest.fixture
def rol_de_proyecto():
    rol = RolDeProyecto(nombre='Desarrollador', descripcion='Descripcion del rol')
    rol.save()
    rol.asignar_permisos(list(Permission.objects.all().filter(codename__startswith='pp_')))
    return rol


@pytest.fixture
def proyecto(usuario, gerente, rol_de_proyecto):
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba', fecha_de_creacion=timezone.now(),
                        gerente=gerente, creador=usuario, estado=EstadoDeProyecto.CONFIGURACION)
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
    participante.asignar_rol_de_proyecto(rol_de_proyecto)
    participante.save()
    return proyecto


@pytest.mark.django_db
class TestModeloProyecto:
    """
    Pruebas unitarias que comprueban el funcionamiento de los metodos del Modelo Proyecto.
    """
    # TODO: Marcelo test get_participante
    def test_get_participantes(self, proyecto):
        """
        Prueba unitaria encargada de verificar que la funcion get_participantes retorne correctamente los participantes
        de un proyecto.

        Se espera:
            Que get_participantes retorne todos los participantes del Proyecto.

        Mensaje de error:
            No se retornaron correctamente los participantes del Proyecto
        """

        participantes = list(Participante.objects.all().filter(proyecto=proyecto))
        gerente = proyecto.participante_set.filter(usuario=proyecto.gerente)
        print([g.usuario for g in gerente])
        assert list(
            proyecto.get_participantes()) == participantes, 'No se retornaron correctamente los participantes del' \
                                                            'Proyecto'

    # TODO: Marcelo test get_comite_de_cambios
    # TODO: Marcelo test get_fases
    def test_asignar_rol_de_proyecto(self, proyecto, usuario, rol_de_proyecto):
        """
        Prueba que verifica la asignacion correcta de un rol de proyecto a un usuario.

        Se espera:
            Que el usuario tenga un rol asignado y tenga los permisos de proyecto asignados.

        Mensaje de Error:
            El rol no ha sido asignado al participante o no se han asignado los permisos correspondientes
            al participante
        """
        permisos = list(rol_de_proyecto.permisos.all())
        fases = list(Fase.objects.all().filter(proyecto=proyecto))
        permisos_por_fase = {fases[0]: permisos}
        print(proyecto.participante_set.all()[0].usuario == usuario)
        proyecto.asignar_rol_de_proyecto(usuario, rol_de_proyecto, permisos_por_fase)
        # Comprobacion de postcondicion
        condicion = proyecto.participante_set.get(usuario=usuario).rol == rol_de_proyecto
        condicion = condicion and proyecto.participante_set.get(usuario=usuario).permisos_por_fase.all().exists()
        assert condicion is True, 'El rol no ha sido asignado al participante o no se han asignado los permisos ' \
                                  'correspondientes al participante'

    def test_tiene_permiso_de_proyecto(self, proyecto, usuario, rol_de_proyecto):
        """
        Test que verifica que el metodo tiene_permiso_de_proyecto de la clase Proyecto retorne verdadero si el
        usuario no cuenta con el permiso dado.

        Se espera:
            Que tiene_permiso_de_proyecto retorne True.

        Mensaje de Error:
            El metodo indica que el usuario no tiene el permiso de proyecto pero el usuario si tiene asignado el permiso.
        """
        fases = proyecto.fase_set.all()
        permisos = list(rol_de_proyecto.get_pp_por_fase())
        permisos_por_fase = {fases[0]: permisos}
        proyecto.asignar_rol_de_proyecto(usuario, rol_de_proyecto, permisos_por_fase)

        condicion = proyecto.tiene_permiso_de_proyecto(usuario, 'pp_agregar_participante')
        assert condicion is True, 'El metodo indica que el usuario no tiene el permiso de proyecto pero el usuario si ' \
                                  'tiene asignado el permiso'

    def test_tiene_no_permiso_de_proyecto(self, proyecto, usuario, rol_de_proyecto):
        """
        Test que verifica que el metodo tiene_permiso_de_proyecto de la clase Proyecto retorne falso si el
        usuario no cuenta con el permiso dado.

        Se espera:
            Que tiene_permiso_de_proyecto retorne False.

        Mensaje de Error:
            El metodo indica que el usuario tiene el permiso de proyecto pero el usuario no tiene asignado el permiso.
        """
        fases = Fase.objects.all().filter(proyecto=proyecto)
        permisos = list(rol_de_proyecto.get_pp_por_fase())
        permisos_por_fase = {fases[0]: permisos}
        proyecto.asignar_rol_de_proyecto(usuario, rol_de_proyecto, permisos_por_fase)

        condicion = proyecto.tiene_permiso_de_proyecto(usuario, 'pp_permiso_no_existente')
        assert condicion is False, 'El metodo indica que el usuario tiene el permiso de proyecto pero el usuario no ' \
                                   'tiene asignado el permiso'

    # TODO: Marcelo test tiene_permiso_de_proyecto_en_fase

    def test_cancelar_proyecto_en_configuracion(self, usuario, rol_de_proyecto):
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

    def test_cancelar_proyecto_iniciado(self, usuario, rol_de_proyecto):
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

    def test_cancelar_proyecto_finalizado(self, usuario, rol_de_proyecto):
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

    def test_iniciar_proyecto_en_configuracion_sin_fases(self, usuario, rol_de_proyecto):
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
        try:
            proyecto_prueba.iniciar()
        except:
            pass
        assert proyecto_prueba.estado == EstadoDeProyecto.CONFIGURACION, 'No se puede Iniciar el Proyecto sin fases'

    def test_iniciar_proyecto_en_configuracion(self, usuario, rol_de_proyecto):
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

    # TODO: Hugo test eliminar_participante


@pytest.mark.django_db
class TestModeloParticipante:
    """
    Pruebas unitarias que comprueban el funcionamiento de los metodos de la clase Participante.
    """
    # TODO: Marcelo test get_rol_nombre
    # TODO: Marcelo test  get_pp_por_fase
    # TODO: Marcelo test asignar_permisos_de_proyecto
    # TODO: Marcelo test asignar_rol_de_proyecto
    # TODO: Marcelo test tiene_rol
    # TODO: Marcelo test tiene_pp_en_fase
    @pytest.mark.parametrize('permiso,esperado', [('pp_cerrar_fase', True), ('pp_agregar_items', True)])
    def test_participante_tiene_permiso_gerente(self, proyecto, permiso, esperado):
        """
        Prueba unitaria que verifica el funcionamiento correcto del metodo tiene_pp cuando se lo invoca desde
        del Participante Gerente del Proyecto.

        Se espera:
            Que el metodo retorne True para todos los casos.

        Mensaje de Error:
            El metodo deberia retornar True, pero retorno False

        """
        gerente = proyecto.get_gerente()
        participante_gerente = Participante.objects.get(usuario=gerente)

        assert participante_gerente.tiene_pp(permiso) == esperado, 'El metodo deberia retornar True, pero retorno False'

    @pytest.mark.parametrize('permiso,esperado', [('pp_cerrar_fase', False), ('pp_agregar_items', False),
                                                  ('pp_agregar_participante', True), ('pp_eliminar_participante', True),
                                                  ('pp_asignar_rp_a_participante', True)])
    def test_participante_tiene_permiso(self, usuario, proyecto, rol_de_proyecto, permiso, esperado):
        """
        Prueba unitaria parametrizada que comprueba el funcionamiento de la funcion tiene_permiso de la clase Participante.

        Esta prueba comprueba con varios permisos de proyecto si el usuario tiene permisos.

        Se espera:
            Que para cada uno de los siguientes casos el metodo lance la siguiente respuesta.

                - 'pp_cerrar_fase' -> False\n
                - 'pp_agregar_items' -> False\n
                - 'pp_agregar_participante' -> True\n
                - 'pp_eliminar_participante' -> True\n
                - 'pp_asignar_rp_a_participante' -> True

        Mensaje de Error:
            Se espera que la verificacion de si el participante tiene el Permiso {permiso} resulte en {esperado},
            pero resulto {valor_obtenido}
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

    # TODO: Marcelo test tiene_pp_en_fase
    # TODO: Marcelo test get_permisos_de_proyecto_list
    # TODO: Marcelo test get_permisos_por_fase_list


@pytest.mark.django_db
class TestModeloComite:
    # TODO: Hugo test es_miembro

    pass


@pytest.mark.django_db
class TestVistasProyecto:
    """
    Pruebas unitarias que comprueban el funcionamiento de las vistas referentes a un Proyecto.
    """
    @pytest.fixture
    def gerente_loggeado(self, gerente):
        client = Client()
        client.login(username='gerente', password='password123')
        return client

    # TODO: Luis test nuevo_proyecto_view
    # TODO: Hugo test participantes_view
    # TODO: Hugo test participante_view
    # TODO: Hugo test eliminar_participante_view
    # TODO: Luis test visualizar_proyecto_view
    # TODO: Luis test editar_proyecto_view
    # TODO: Luis test cancelar_proyecto_view
    # TODO: Luis test iniciar_proyecto_view

    def test_nuevo_participante_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista para agregar un nuevo participante a un proyecto.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        print(gerente_loggeado)
        response = gerente_loggeado.get(reverse('nuevo_participante', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_asignar_rol_de_proyecto_view(self, gerente_loggeado, proyecto, usuario):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista de asignación de un nuevo rol de proyecto a un participante.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """
        participante = proyecto.get_participante(usuario)
        response = gerente_loggeado.get(reverse('asignar_rol_de_proyecto', args=(proyecto.id, participante.id)))
        assert response.status_code == HTTPStatus.OK, f'Hubo un error al tratar de acceder a la URL {response.content}'

    # TODO: Hugo test seleccionar_miembros_del_comite_view
    # TODO: Marcos test info_proyecto_view
    pass

