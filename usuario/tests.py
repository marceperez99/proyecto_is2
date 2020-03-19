from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus
import pytest

# Create your tests here.
@pytest.mark.django_db
def test_ver_usuario_existente():
    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    client = Client()
    client.login(username='testing', password='12345')

    response = client.get(reverse('usuario', args=(user.id,)))
    assert response.status_code == HTTPStatus.OK, 'No se puede acceder a \'usuarios/id\' para un usuario existente.'


@pytest.mark.django_db
def test_ver_usuario_no_existente():
    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    client = Client()
    client.login(username='testing', password='12345')

    response = client.get(reverse('usuario', args=(user.id+1,)))
    assert response.status_code == HTTPStatus.NOT_FOUND, 'El sistema muestra información de un usuario no existente.'


@pytest.mark.django_db
def test_ver_usuarios():
    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    client = Client()
    client.login(username='testing', password='12345')

    response = client.get(reverse('usuarios'))
    assert response.status_code == HTTPStatus.OK, 'No es posible visualizar la lista de usuarios'