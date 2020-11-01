from http import HTTPStatus

import pytest
from django.contrib.auth.models import User, Permission
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante, EstadoDeProyecto, Comite
from gestion_de_proyecto.tests.factories import proyecto_factory
from roles_de_proyecto.models import RolDeProyecto
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
def usuario2(rs_admin):
    return user_factory('usuario2_test', 'password123', 'user2@email.com', rs_admin.nombre)


@pytest.fixture
def gerente(rs_admin):
    return user_factory('gerente', 'password123', 'gerente@email.com', rs_admin.nombre)


@pytest.fixture
def rol_de_proyecto():
    return rol_de_proyecto_factory({
        'nombre': 'Desarrollador',
        'descripcion': 'Descripcion del Rol',
        'permisos': [p.codename for p in Permission.objects.all().filter(codename__startswith='pp_')]
    })


@pytest.fixture
def proyecto(usuario, gerente, rol_de_proyecto):
    return proyecto_factory({
        'nombre': 'Proyecto de Prueba',
        'descripcion': 'Descripcion de Prueba',
        'creador': usuario.username,
        'gerente': gerente.username,
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
        'participantes': [
            {
                'usuario': usuario.username,
                'rol_de_proyecto': 'Desarrollador',
                'permisos': {}
            }
        ]
    })


@pytest.mark.django_db
class TestModeloProyecto:
    """
    Pruebas unitarias que comprueban el funcionamiento de los metodos del Modelo Proyecto.
    """

    def test_get_participante(self, proyecto, usuario):
        """
        Prueba unitaria que comprueba que el metodo get_participante retorne correctamente el Objeto Participante
         dado un usuario.

        Se espera:
            Que get_participante retorne correctamente el objecto Participante de un usuario dentro de un
            proyecto.

        Mensaje de error:
            No se retornaron correctamente los participantes del Proyecto
        """
        participante = proyecto.get_participante(usuario)
        assert participante is not None and participante.usuario.id == usuario.id

    def test_get_participante_gerente(self, proyecto, gerente):
        """
        Prueba unitaria que comprueba que el metodo get_participante retorne correctamente el Objeto Participante
         dado un usuario.

        Se espera:
            Que get_participante retorne correctamente el objecto Participante de un usuario dentro de un
            proyecto.

        Mensaje de error:
            No se consiguió correctamente el objecto participante del Gerente del Proyecto.
        """
        participante = proyecto.get_participante(gerente)
        condicion = participante is not None and participante.usuario.id == gerente.id
        assert condicion is True, "No se consiguió correctamente el objecto participante del Gerente del Proyecto."

    def test_get_participante_no_existente(self, proyecto):
        """
        Prueba unitaria que comprueba que el metodo get_participante retorne None al tratar de obtener el Objeto
        Participante de un usuario que no está dentro de un Proyecto.

        Se espera:
            Que get_participante retorne None.

        Mensaje de error:
            El método get_participante debe retornar None cuando se le pasa un usuario que no está dentro del Proyecto.
        """
        user = User(username='usuario1', email='usuario1@gmail.com')
        user.set_password('password123')
        user.save()

        participante = proyecto.get_participante(user)
        assert participante is None, "El método get_participante debe retornar None cuando se le pasa un usuario" \
                                     " que no está dentro del Proyecto"

    def test_get_participante_usuario_sin_rol(self, proyecto):
        """
        Prueba unitaria que comprueba que el metodo get_participante retorne None al tratar de obtener el Objeto
        Participante participante que no tiene un rol dentro del Proyecto.

        Se espera:
            Que get_participante retorne None.

        Mensaje de error:
            El método get_participante debe retornar None cuando se le pasa un usuario que no tiene
            un rol dentro del Proyecto.
        """
        user = User(username='usuario1', email='usuario1@gmail.com')
        user.set_password('password123')
        user.save()
        Participante.objects.create(usuario=user, proyecto=proyecto)

        participante = proyecto.get_participante(user)
        assert participante is None, "El método get_participante debe retornar None cuando se le pasa un usuario" \
                                     " que no tiene un rol dentro del Proyecto"

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

        assert list(
            proyecto.get_participantes()) == participantes, 'No se retornaron correctamente los participantes del' \
                                                            'Proyecto'

    def test_get_comite_de_cambios(self, proyecto, usuario, gerente):
        """
        Prueba unitaria que comprueba el funcionamiento del metodo get_comite_de_cambios del Modelo Proyecto.

        Se espera:
            Que el método retorne el objeto Comite que representa el comite de cambios del Proyecto.

        Mensaje de Error:
            No se obtuvo correctamente el Comite del Proyecto.
        """
        participantes = proyecto.get_participantes()
        comite = Comite.objects.create(proyecto=proyecto)
        comite.miembros.add(*participantes)

        comite = proyecto.get_comite_de_cambios()

        condicion = all(part in participantes for part in comite.miembros.all())
        assert condicion is True, "No se obtuvo correctamente el Comite del Proyecto."

    def test_get_fases(self, proyecto):
        """
        Prueba unitaria que comprueba que el metodo get_fases de un Proyecto obtenga correctamente todas las fases de
        un Proyecto.

        Se espera:

        Mensaje de Error:
            No se retornaron todas las fases del proyecto o estos no estan en el orden correcto
        """
        fases = proyecto.get_fases()
        # Se comprueban que todas las fases retornadas estén dentro de las fases del proyecto
        # y ordenadas por fase_anterior
        condicion = all(fase in fases for fase in proyecto.fase_set.all()) and all(
            fase.fase_anterior is None if i == 0 else fase.fase_anterior.id == fases[i - 1].id for i, fase in
            enumerate(fases))
        assert condicion is True, "No se retornaron todas las fases del proyecto o estos no estan en el orden correcto"

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
            El metodo indica que el usuario no tiene el permiso de proyecto pero el usuario si tiene
            asignado el permiso.
        """
        fases = proyecto.fase_set.all()
        permisos = list(rol_de_proyecto.get_pp_por_fase())
        permisos_por_fase = {fases[0]: permisos}
        proyecto.asignar_rol_de_proyecto(usuario, rol_de_proyecto, permisos_por_fase)

        condicion = proyecto.tiene_permiso_de_proyecto(usuario, 'pp_agregar_participante')
        assert condicion is True, 'El metodo indica que el usuario no tiene el permiso de proyecto pero el ' \
                                  'usuario si tiene asignado el permiso'

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

    @pytest.mark.parametrize('permiso, fase, esperado', [('pp_f_crear_tipo_de_item', 'Analisis', True),
                                                         ('pp_f_editar_tipo_de_item', 'Desarrollo', False)])
    def test_tiene_permiso_de_proyecto_en_fase(self, proyecto, usuario, permiso, fase, esperado):
        """
        Test que verifica que el metodo tiene_permiso_de_proyecto_en_fase de la clase Proyecto retorne falso si el
        usuario no cuenta con el permiso dado dentro de una fase.

        Se espera:
            Que tiene_permiso_de_proyecto retorne para:
                'pp_f_crear_tipo_de_item', 'Analisis' -> True
                'pp_f_editar_tipo_de_item', 'Desarrollo' -> False

        Mensaje de Error:
            Se esperaba que el metodo retorne {esperado} pero se retornó {tiene_permiso}.
        """
        fase = proyecto.fase_set.get(nombre=fase)
        permisos = Permission.objects.all().filter(codename__startswith='pp_')
        fases = proyecto.get_fases()
        participante = proyecto.get_participante(usuario)
        rol = RolDeProyecto.objects.create(nombre="Rol1", descripcion="Descripcion")
        rol.permisos.add(*permisos)
        permisos_por_fase = {fases[0]: list(permisos)}
        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)

        tiene_permiso = proyecto.tiene_permiso_de_proyecto_en_fase(usuario, fase, permiso)

        assert tiene_permiso == esperado, f'Se esperaba que el metodo retorne {esperado} ' \
                                          f'pero se retorno {tiene_permiso}'

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
        assert proyecto_prueba.estado == EstadoDeProyecto.FINALIZADO, "No se puede cambiar el estado de un " \
                                                                      "proyecto con estado Finalizado"

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
        Prueba unitaria para verificar que al momento de iniciar un proyecto con al menos una fase y un comite de
        cambios, este cambie de estado "En Configuracion", a "Iniciado".

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

    def test_eliminar_participante(self, proyecto, usuario):
        """
        Prueba unitaria que verifica el funcionamiento de eliminar participante.

        Resultado Esperado:
            - El usuario ya no es un participante del proyecto.

        Mensaje de Error:
            - El participante no ha sido eliminado correctamente
        """
        proyecto.eliminar_participante(usuario)
        participante = proyecto.get_participante(usuario)
        assert participante is None, 'El participante no ha sido eliminado correctamente'

    @pytest.mark.parametrize("fase1_cerrada,fase2_cerrada,fase3_cerrada, resultado",
                             [(False, False, False, ['Analisis', 'Desarrollo', 'Pruebas']),
                              (True, False, False, ['Desarrollo', 'Pruebas']),
                              (True, True, False, ['Pruebas'])])
    def test_finalizar_proyecto_fallo(self, proyecto, fase1_cerrada, fase2_cerrada, fase3_cerrada, resultado):
        """
        Prueba unitaria que comprueba el funcionamiento correcto del metodo encargado de finalizar
        un proyecto en el caso de que no se pueda finalizar el proyecto
        Se espera:
            | Que el proyecto se mantenga en el estado "Iniciado" y el metodo lance una excepcion con
            | las fases que no estan cerradas.

        Mensaje de error:
            El metodo deberia lanzar una excepcion con los siguientes valores
        """
        fases = proyecto.get_fases()
        fases[0].fase_cerrada = fase1_cerrada
        fases[0].save()
        fases[1].fase_cerrada = fase2_cerrada
        fases[1].save()
        fases[2].fase_cerrada = fase3_cerrada
        fases[2].save()
        with pytest.raises(Exception) as excinfo:
            proyecto.finalizar()
        condicion = all(fase in resultado for fase in list(excinfo.value.args)[0]) and \
                    all(fase in list(excinfo.value.args)[0] for fase in resultado)
        assert condicion, f'El metodo deberia lanzar una excepcion con los siguientes valores:{resultado} pero lanzo: {list(excinfo.value.args)[0]}'

    def test_finalizar_proyecto_exito(self, proyecto):
        """
        Prueba unitaria que comprueba el funcionamiento correcto del metodo encargado de finalizar
        un proyecto
        Se espera:
            Que el proyecto quede en estado "Finalizado".

        Mensaje de error:
            El Proyecto no fue finalizado
        """
        for fase in proyecto.get_fases():
            fase.fase_cerrada = True
            fase.save()

        proyecto.finalizar()
        proyecto.refresh_from_db()
        assert proyecto.estado == EstadoDeProyecto.FINALIZADO, f"El Proyecto no fue finalizado"


@pytest.mark.django_db
class TestModeloParticipante:
    """
    Pruebas unitarias que comprueban el funcionamiento de los metodos de la clase Participante.
    """

    def test_get_pp_por_fase(self, proyecto, usuario):
        """
        Test que verifica que el metodo tget_pp_por_fase retorne correctamente todos los permisos que tiene el usuario
        en cada fase.

        Se espera:
            Que el metodo retorne un diccionario con todos los permisos por fase que tiene el usuario en cada fase.

        Mensaje de Error:
            No se obtuvo correctamente la lista de permisos por fase del usuario.
        """
        participante = proyecto.get_participante(usuario)
        fases = proyecto.get_fases()

        rol = RolDeProyecto.objects.create(nombre="Rol2", descripcion="Descripcion")
        permisos = Permission.objects.all().filter(codename__startswith='pp_f')
        rol.permisos.add(*permisos)
        permisos_por_fase = {fases[0]: list(permisos), fases[1]: [], fases[2]: []}

        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)
        resultado = participante.get_pp_por_fase()
        resultado = {k: list(v) for k, v in resultado.items()}
        condicion = all(all(perm in permisos_por_fase[k] for perm in v) and
                        all(perm in v for perm in permisos_por_fase[k]) for k, v in resultado.items())
        assert condicion is True, 'No se obtuvo correctamente la lista de permisos por fase del usuario'

    def test_asignar_permisos_de_proyecto(self, proyecto, usuario):
        """
        Prueba unitaria que comprueba que el metodo asignar_permisos_de_proyecto asigne correctamente los permisos
        de proyecto por fase.

        Se espera:
            Que tiene_permiso_de_proyecto asigne correctamente, por cada fase, los permisos pasados.

        Mensaje de Error:
            El metodo no retornó correctamente la lista de permisos o no se retornaron todos los permisos.
        """
        participante = proyecto.get_participante(usuario)
        fases = proyecto.get_fases()
        permisos = list(Permission.objects.filter(codename__startswith='pp_f_'))
        permisos_por_fase = {fases[0]: permisos, fases[1]: [], fases[2]: permisos}

        participante.asignar_permisos_de_proyecto(permisos_por_fase)

        permisos_fases_result = {ppf.fase: list(ppf.permisos.all()) for ppf in participante.permisos_por_fase.all()}

        condicion = all(all(p in permisos_por_fase[fase] for p in perms)
                        for fase, perms in permisos_fases_result.items())
        condicion = condicion and all(all(p in permisos_fases_result[fase] for p in perms)
                                      for fase, perms in permisos_por_fase.items())
        assert condicion is True, 'El metodo no retornó correctamente la lista de permisos o ' \
                                  'no se retornaron todos los permisos'

    def test_asignar_rol_de_proyecto(self, proyecto, usuario):
        """
        Test que verifica el funcionamiento del metodo asignar_rol_de_pryoecto de la clase Participante.

        Se espera:
            Que asignar_rol_de_proyecto asigne correctamente el rol de Proyecto al Participante.

        Mensaje de Error:
            El metodo no asignó correctamente el rol de proyecto al participante.
        """
        participante = proyecto.get_participante(usuario)
        participante.rol = None
        participante.save()
        fases = proyecto.get_fases()
        rol = RolDeProyecto.objects.create(nombre="Rol2", descripcion="Descripcion")
        permisos = Permission.objects.all().filter(codename__startswith='pp_f')
        rol.permisos.add(*permisos)
        permisos_por_fase = {fases[0]: list(permisos), fases[1]: [], fases[2]: []}

        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)
        condicion = participante.rol is not None
        assert condicion is True, 'El metodo no asignó correctamente el rol de proyecto al participante'

    @pytest.mark.parametrize('permiso,esperado', [('pp_cerrar_fase', False), ('pp_agregar_items', False)])
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

    @pytest.mark.parametrize('permiso, fase, esperado', [('pp_f_crear_tipo_de_item', 'Analisis', True),
                                                         ('pp_f_editar_tipo_de_item', 'Desarrollo', False)])
    def test_tiene_pp_en_fase(self, proyecto, usuario, permiso, fase, esperado):
        """
        Test que verifica el funcionamiento del metodo tiene_pp_en_fase de la clase Participante.

        Se espera:
            Que tiene_permiso_de_proyecto retorne para:
                'pp_f_crear_tipo_de_item', 'Analisis' -> True
                'pp_f_editar_tipo_de_item', 'Desarrollo' -> False

        Mensaje de Error:
            Se esperaba que el metodo retorne {esperado} pero se retornó {tiene_permiso}.
        """
        fase = proyecto.fase_set.get(nombre=fase)
        permisos = Permission.objects.all().filter(codename__startswith='pp_')
        fases = proyecto.get_fases()
        rol = RolDeProyecto.objects.create(nombre="Rol1", descripcion="Descripcion")
        rol.permisos.add(*permisos)
        permisos_por_fase = {fases[0]: list(permisos)}
        participante = proyecto.get_participante(usuario)
        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)

        tiene_permiso = participante.tiene_pp_en_fase(fase, permiso)

        assert tiene_permiso == esperado, f'Se esperaba que el metodo retorne {esperado} pero se retorno {tiene_permiso}'

    def test_get_permisos_de_proyecto_list(self, proyecto, usuario):
        """
        Test que verifica el funcionamiento del metodo get_permisos_de_proyecto_list de la clase Participante.

        Se espera:
            Que tiene_permiso_de_proyecto retorne una lista con los codenames de los Permisos con los que cuenta el
            participante.

        Mensaje de Error:
            El metodo no retornó correctamente la lista de permisos o no se retornaron todos los permisos.
        """
        participante = proyecto.get_participante(usuario)
        permisos = [perm.codename for perm in Permission.objects.all().filter(codename__startswith='pp_')
            .exclude(codename__startswith='pp_f')]

        permisos_test = participante.get_permisos_de_proyecto_list()

        condicion = all(perm in permisos for perm in permisos_test) and all(perm in permisos_test for perm in permisos)
        assert condicion is True, 'El metodo no retornó correctamente la lista de permisos o ' \
                                  'no se retornaron todos los permisos'

    @pytest.mark.parametrize('fase, esperado',
                             [('Analisis', ['pp_f_editar_tipo_de_item', 'pp_f_crear_tipo_de_item', 'pu_f_ver_fase']),
                              ('Desarrollo', [])])
    def test_get_permisos_por_fase_list(self, proyecto, usuario, fase, esperado):
        """
        Test que verifica que el metodo tiene_permiso_de_proyecto_en_fase de la clase Proyecto retorne falso si el
        usuario no cuenta con el permiso dado dentro de una fase.

        Se espera:
            Que get_permisos_por fase retorne para:
                'Analisis' -> ['pp_f_editar_tipo_de_item', 'pp_f_crear_tipo_de_item', 'pu_f_ver_fase']
                'Desarrollo' -> []

        Mensaje de Error:
            Se esperaba que el metodo retorne {esperado} pero se retornó {lista_permisos}.
        """
        fase = proyecto.fase_set.get(nombre=fase)

        permisos = [Permission.objects.get(codename='pp_f_editar_tipo_de_item'),
                    Permission.objects.get(codename='pp_f_crear_tipo_de_item'),
                    Permission.objects.get(codename='pu_f_ver_fase')]

        fases = proyecto.get_fases()
        participante = proyecto.get_participante(usuario)
        rol = RolDeProyecto.objects.create(nombre="Rol1", descripcion="Descripcion")
        rol.permisos.add(*permisos)
        permisos_por_fase = {fases[0]: list(permisos)}
        participante.asignar_rol_de_proyecto(rol, permisos_por_fase)

        lista_permisos = participante.get_permisos_por_fase_list(fase)

        condicion = all(p in esperado for p in lista_permisos) and all(p in lista_permisos for p in esperado)
        assert condicion is True, 'Se esperaba que el metodo retorne {esperado} pero se retornó {lista_permisos}'


@pytest.mark.django_db
class TestModeloComite:
    """
    Pruebas unitarias que verifican el correcto funcionamiento del modelo comite
    """

    def test_es_miembro(self, proyecto, usuario):
        """
        Prueba unitaria que verifica el funcionamiento del método es_miembro de un comite.

        Resultado Esperado:
            - El método retorna True debido a que el participante es miembro del comite.

        Mensaje de error:
            - El método es_miembro de un comite no reconoce al usuario

        """
        comite = Comite()
        comite.proyecto = proyecto
        comite.save()
        participante = proyecto.get_participante(usuario)
        comite.miembros.add(participante)
        assert comite.es_miembro(participante) == True, 'El método es_miembro de un comite no reconoce al usuario'

    def test_no_es_miembro(self, proyecto, usuario):
        """
        Prueba unitaria que verifica el funcionamiento del método es_miembro de un comite.

        Resultado Esperado:
            - El método retorna False debido a que el participante no es miembro del comite.

        Mensaje de error:
            - El método es_miembro de un comite reconoce al usuario como miembro erroneamente

        """
        comite = Comite()
        comite.proyecto = proyecto
        comite.save()
        participante = proyecto.get_participante(usuario)

        assert comite.es_miembro(
            participante) == False, 'El método es_miembro de un comite reconoce al usuario como miembro erroneamente'


@pytest.mark.django_db
class TestVistasProyecto:
    """
    Pruebas unitarias correspondientes al funcionamiento correcto de las Vistas relacionadas a Proyectos.
    """

    @pytest.fixture
    def gerente_loggeado(self, gerente):
        client = Client()
        client.login(username='gerente', password='password123')
        return client

    def test_nuevo_proyecto_view(self, gerente_loggeado):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de nuevo proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - Hubo un error al tratar de acceder a la URL
        """
        response = gerente_loggeado.get(reverse('nuevo_proyecto'))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_participantes_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de ver participantes de un proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL

        """
        response = gerente_loggeado.get(reverse('participantes', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_participante_view(self, gerente_loggeado, proyecto, usuario):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de ver un participante de un proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL

        """
        participante = proyecto.get_participante(usuario)
        response = gerente_loggeado.get(reverse('participante', args=(proyecto.id, participante.id)))

        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_eliminar_participante_view(self, gerente_loggeado, proyecto, usuario):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de eliminar un participante de un proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL

        """
        comite = Comite()
        comite.proyecto = proyecto
        comite.save()
        participante = proyecto.get_participante(usuario)

        response = gerente_loggeado.get(reverse('eliminar_participante', args=(proyecto.id, participante.id)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL '

    def test_editar_proyecto_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de editar proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - Hubo un error al tratar de acceder a la URL

        """
        response = gerente_loggeado.get(reverse('editar_proyecto', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    @pytest.mark.parametrize('estado_proyecto', [EstadoDeProyecto.CONFIGURACION,
                                                 EstadoDeProyecto.INICIADO,
                                                 ])
    def test_cancelar_proyecto_view(self, gerente_loggeado, proyecto, estado_proyecto):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de cancelar proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - Hubo un error al tratar de acceder a la URL

        """
        proyecto.estado = estado_proyecto
        proyecto.save()
        response = gerente_loggeado.get(reverse('cancelar_proyecto', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_iniciar_proyecto_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de iniciar proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - Hubo un error al tratar de acceder a la URL

        """
        response = gerente_loggeado.get(reverse('iniciar_proyecto', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_visualizar_proyecto_view(self, gerente_loggeado, gerente, usuario, usuario2):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de visualizar proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - Hubo un error al tratar de acceder a la URL

        """
        rol_de_proyecto = rol_de_proyecto_factory({
            'nombre': 'rol',
            'descripcion': 'descripcion',
            'permisos': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
        })
        proyecto = proyecto_factory({
            'gerente': 'gerente',
            'nombre': 'Proyecto',
            'estado': 'Iniciado',
            'descripcion': 'Proyecto de prueba',
            'creador': 'gerente',
            'fases': [
                {
                    'nombre': 'Fase 1',
                    'descripcion': 'Descripcion fase 1',
                    'puede_cerrarse': False,
                    'fase_cerrada': False,
                }, {
                    'nombre': 'Fase 2',
                    'descripcion': 'Descripcion fase 2',
                    'puede_cerrarse': False,
                    'fase_cerrada': False,
                }, {
                    'nombre': 'Fase 3',
                    'descripcion': 'Descripcion fase 3',
                    'puede_cerrarse': False,
                    'fase_cerrada': False,
                }
            ],
            'participantes': [
                {
                    'usuario': 'usuario_test',
                    'rol_de_proyecto': 'rol',
                    'permisos': {
                        'Fase 1': ['pp_ver_participante', 'pp_agregar_participante'],
                        'Fase 2': ['pp_ver_participante', 'pp_agregar_participante'],
                        'Fase 3': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
                    }
                },
                {
                    'usuario': 'usuario2_test',
                    'rol_de_proyecto': 'rol',
                    'permisos': {
                        'Fase 1': ['pp_ver_participante', 'pp_agregar_participante'],
                        'Fase 2': ['pp_ver_participante', 'pp_agregar_participante'],
                        'Fase 3': ['pp_ver_participante', 'pp_agregar_participante', 'pp_eliminar_participante']
                    }
                }
            ],
            'comite_de_cambios': ['gerente', 'usuario_test', 'usuario2_test', ]
        })
        response = gerente_loggeado.get(reverse('visualizar_proyecto', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL'

    def test_nuevo_participante_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria encargada de comprobar que no se presente ningún error a la hora de mostrar la
        vista para agregar un nuevo participante a un proyecto.

        Se espera:
            Que la respuesta HTTP sea OK.

        Mensaje de Error:
            Hubo un error al tratar de acceder a la URL
        """

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

    def test_seleccionar_miembros_del_comite_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de seleccionar miembros del comite.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL

        """
        comite = Comite()
        comite.proyecto = proyecto
        comite.save()
        response = gerente_loggeado.get(reverse('asignar_miembros_comite', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL '

    def test_info_proyecto_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria que comprueba que no exista error al acceder a la URL de ver informacion del proyecto.

        Resultado Esperado:
            - Una respuesta HTTP con codigo de estado 200

        Mensaje de Error:
            - No es posible acceder a la URL

        """
        comite = Comite()
        comite.proyecto = proyecto
        comite.save()
        response = gerente_loggeado.get(reverse('info_proyecto', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL '

    def test_finalizar_proyecto_view(self, gerente_loggeado, proyecto):
        """
        Prueba unitaria que comprueba el funcionamiento correcto de la vista de finalizacion de proyecto

        Se espera:
            HttpResponse OK

        Mensaje de error:
            Hubo un error al tratar de acceder a la URL de finalizacion de proyecto
        """
        proyecto.estado = EstadoDeProyecto.INICIADO
        proyecto.save()
        response = gerente_loggeado.get(reverse('finalizar_proyecto', args=(proyecto.id,)))
        assert response.status_code == HTTPStatus.OK, 'Hubo un error al tratar de acceder a la URL ' \
                                                      'de finalizacion de proyecto'
