"""
    Configuraciones del proyecto a ser usadas en un entorno de Produccion
"""
from dotenv import load_dotenv
from .base import *

ENVIROMENT_VARIABLES_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'auth', '.env')
load_dotenv(ENVIROMENT_VARIABLES_PATH)
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG_VALUE')

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USUARIO'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'DATABASE_PORT': os.environ.get('DB_PORT'),

    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT')


# Configuraciones del SSO
GOOGLE_OAUTH_SECRET_KEY = os.environ.get('GOOGLE_OAUTH_SECRET_KEY')
GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')


# Configuracion de Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
