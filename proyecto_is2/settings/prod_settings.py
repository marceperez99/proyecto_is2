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
DEBUG = os.environ.get('DEBUG_VALUE') == 'True'
TESTING = False
ALLOWED_HOSTS = ['*']

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
STATIC_ROOT = os.environ.get('STATIC_ROOT')


# Configuraciones del SSO

# Configuracion del Google Drive Storage
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = os.environ.get('GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE')


# Configuracion de Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')


MEDIA_ROOT = os.environ.get("MEDIA_ROOT")
MEDIA_URL = os.environ.get("MEDIA_URL")

# Configuracion de Correo de envio de correos electronicos
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS') == "True"