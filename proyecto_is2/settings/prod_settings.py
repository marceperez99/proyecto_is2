"""
    Configuraciones del proyecto a ser usadas en un entorno de Produccion
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$ce2p+5(x@x!)8f7sqd*bmq30(b@dr!kr!55_1oz2f%1x%but$'#os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../../db.sqlite3'),

    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/proyecto_is2/site/public/'