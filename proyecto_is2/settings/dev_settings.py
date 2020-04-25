"""
    Configuraciones del proyecto a ser usadas en un entorno de Desarrollo

"""
from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$ce2p+5(x@x!)8f7sqd*bmq30(b@dr!kr!55_1oz2f%1x%but$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'proyecto_is2_dev',
        'USER': 'proyecto_user_test',
        'PASSWORD': 'Pr0yect0Test',
        'HOST': 'localhost',
        'DATABASE_PORT': '5432',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles/'

# Configuraciones del SSO
GOOGLE_OAUTH_SECRET_KEY = 'sw2lVjRDgG1GtDAZVC_QmVhr'
GOOGLE_OAUTH_CLIENT_ID = '347886323853-r72mjg1utuabev2f73ngef3tg2nqluth.apps.googleusercontent.com'
