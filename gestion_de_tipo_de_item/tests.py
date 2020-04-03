import pytest
from django.contrib.auth.models import User, Permission
from django.test import Client
# Create your tests here.
from django.utils import timezone

from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Proyecto, Participante
from gestion_de_tipo_de_item.forms import AtributoCadenaForm, AtributoArchivoForm, AtributoBooleanoForm, \
    AtributoNumericoForm, AtributoFechaForm
from gestion_de_tipo_de_item.models import TipoDeItem, AtributoBinario, AtributoCadena, AtributoNumerico, AtributoFecha, \
    AtributoBooleano
from gestion_de_tipo_de_item.utils import recolectar_atributos, atributo_form_handler
from roles_de_proyecto.models import RolDeProyecto


@pytest.fixture
def usuario():
    user = User(username='user_test', email='test@admin.com')
    user.set_password('password123')
    user.save()
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
    proyecto = Proyecto(nombre='Proyecto Prueba', descripcion='Descripcion de prueba', fecha_de_creacion=timezone.now(),
                        creador=usuario)
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
def atributos(tipo_de_item):
    atributos = []
    abin = AtributoBinario()
    abin.requerido = False
    abin.max_tamaño = 5
    abin.nombre = "Diagrama del caso de uso"
    abin.tipo_de_item = tipo_de_item
    abin.save()

    acad = AtributoCadena()
    acad.nombre = "Descripción"
    acad.requerido = True
    acad.max_longitud = 400
    acad.tipo_de_item = tipo_de_item
    acad.save()

    adate = AtributoFecha()
    adate.nombre = "Fecha de Cierre"
    adate.requerido = True
    adate.tipo_de_item = tipo_de_item
    adate.save()

    anum = AtributoNumerico()
    anum.nombre = "Costo del caso de uso"
    anum.requerido = False
    anum.max_digitos = 2
    anum.max_decimales = 2
    anum.tipo_de_item = tipo_de_item
    anum.save()

    abool = AtributoBooleano()
    abool.nombre = "Cierto"
    abool.requerido = True
    abool.tipo_de_item = tipo_de_item
    abool.save()

    atributos.append(abin)
    atributos.append(acad)
    atributos.append(abool)
    atributos.append(adate)
    atributos.append(anum)
    return atributos


@pytest.mark.django_db
def test_recolectar_atributos(atributos, tipo_de_item):
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


@pytest.mark.django_db
def test_atributo_form_hanldler(atributos, tipo_de_item):
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
