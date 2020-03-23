"""
    Configuraciones del proyecto a ser usadas en un entorno de Produccion
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
#TODO: se debe cambiar esto para obtener el SECRET KEY del entorno
SECRET_KEY = '$ce2p+5(x@x!)8f7sqd*bmq30(b@dr!kr!55_1oz2f%1x%but$'#os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'proyecto_is2',
        'USER': 'proyecto_admin',
        'PASSWORD': 'Pr0yect0Adm1n',
        'HOST': 'localhost',
        'DATABASE_PORT': '5432',

    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/proyecto_is2/site/public/'