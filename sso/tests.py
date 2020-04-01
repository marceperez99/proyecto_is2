from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission, Group
from http import HTTPStatus
import pytest

from roles_de_sistema.models import RolDeSistema


@pytest.fixture
def rs_admin():
    rol = RolDeSistema(nombre='Admin', descripcion='descripcion de prueba')
    rol.save()
    for pp in Permission.objects.filter(content_type__app_label='roles_de_sistema', codename__startswith='p'):
        rol.permisos.add(pp)
    rol.save()
    return rol



def test_index_usuario_no_autenticado():
    client = Client()
    response = client.get(reverse('index'))
    assert response.status_code == HTTPStatus.FOUND

@pytest.mark.django_db
def test_index_usuario_autenticado(rs_admin):
    # Preparacion de entorno para la prueba
    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    user.groups.add(Group.objects.get(name=rs_admin.nombre))
    client = Client()
    client.login(username='testing', password='12345')
    # Prueba de funcionalidad
    response = client.get(reverse('index'))
    assert response.status_code == HTTPStatus.OK

@pytest.mark.django_db
def test_logout():

    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    client = Client()
    client.login(username='testing', password='12345')

    response = client.get(reverse('logout'))
    assert response.status_code == HTTPStatus.FOUND