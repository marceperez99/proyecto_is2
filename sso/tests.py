from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

from http import HTTPStatus

# Create your tests here.
def test_index_usuario_no_autenticado():
    client = Client()
    response = client.get(reverse('index'))
    assert response.status_code == HTTPStatus.FOUND

@pytest.mark.django_db
def test_index_usuario_autenticado():
    #Preparacion de entorno para la prueba
    user = User.objects.create(username='testing')
    user.set_password('12345')
    user.save()
    client = Client()
    client.login(username='testing', password='12345')
    #Prueba de funcionalidad
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