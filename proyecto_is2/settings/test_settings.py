from .dev_settings import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdb',
    }
}
print(os.environ.get('GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS'))
if os.environ.get('GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS'):
    GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = None
    GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS = os.environ.get('GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS')
else:
    GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = f'{BASE_DIR}/proyecto_is2/settings/credenciales/gdriveaccess.json'

