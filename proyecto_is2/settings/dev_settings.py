"""
    Configuraciones del proyecto a ser usadas en un entorno de Desarrollo
"""
from dotenv import load_dotenv

from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
ENV_VARIABLES_PATH = f'{BASE_DIR}/proyecto_is2/settings/credenciales/.env'
load_dotenv(ENV_VARIABLES_PATH)

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
        'NAME': os.environ.get('DB_NOMBRE'),
        'USER': os.environ.get('DB_USUARIO'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'DATABASE_PORT': os.environ.get('DB_PORT'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles/'


# Configuracion del Google Drive Storage
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = f'{BASE_DIR}/proyecto_is2/settings/credenciales/gdriveaccess.json'


# Configuracion de Celery
CELERY_BROKER_URL = 'redis://localhost'

MEDIA_ROOT = f'{BASE_DIR}/media/'
MEDIA_URL = f'{BASE_DIR}/media/items/'

# Configuracion de Correo de envio de correos electronicos
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS') == "True"
