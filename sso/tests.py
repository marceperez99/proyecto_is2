from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission, User, Group
from django.test import Client
from django.urls import reverse

from roles_de_sistema.models import RolDeSistema


# Todo: Comentar
@pytest.fixture
def rs_admin():
    rol = RolDeSistema(nombre='Administrador', descripcion='descripcion de prueba')
    rol.save()
    for pp in Permission.objects.filter(content_type__app_label='roles_de_sistema', codename__startswith='p'):
        rol.permisos.add(pp)
    rol.save()
    return rol


@pytest.mark.django_db
class TestVistasSSO:

    def test_index_usuario_no_autenticado(self):
        """
        Prueba unitaria que comprueba que un usuario no logeado sea redirigido a la vista de inicio de sesion.

        Se espera:
            Que el Status Code de la respuesta del servidor sea HTTPStatus.FOUND.

        Mensaje de Error:
            El status code de la respuesta del servidor no fue HTTPStatus.FOUND.
        """
        client = Client()
        response = client.get(reverse('index'))
        assert response.status_code == HTTPStatus.FOUND, 'El status code de la respuesta del servidor no fue ' \
                                                         'HTTPStatus.FOUND'

    def test_index_usuario_autenticado(self, rs_admin):
        """
        Prueba unitaria que comprueba el funcionaminento correcto de la vista de pantalla de inicio.

        Se espera:
            Que el Status Code de la respuesta del servidor sea HTTPStatus.OK

        Mensaje de Error:
            El status code de la respuesta del servidor no fue HTTPStatus.OK
        """
        # Preparacion de entorno para la prueba
        user = User.objects.create(username='testing')
        user.set_password('12345')
        user.save()
        user.groups.add(Group.objects.get(name=rs_admin.nombre))
        client = Client()
        client.login(username='testing', password='12345')
        # Prueba de funcionalidad
        response = client.get(reverse('index'))
        assert response.status_code == HTTPStatus.OK, 'El status code de la respuesta del servidor no fue HTTPStatus.OK'

    def test_logout(self):
        """
            Prueba unitaria que comprueba el funcionaminento correcto del logout.

            Se espera:
                Que el Status Code de la respuesta del servidor sea HTTPStatus.FOUND

            Mensaje de Error:
                El status code de la respuesta del servidor no fue HTTPStatus.FOUND
            """
        user = User.objects.create(username='testing')
        user.set_password('12345')
        user.save()
        client = Client()
        client.login(username='testing', password='12345')

        response = client.get(reverse('logout'))
        assert response.status_code == HTTPStatus.FOUND, 'El status code de la respuesta del servidor no fue' \
                                                         ' HTTPStatus.FOUND'
