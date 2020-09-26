#!/bin/bash
#Script que construye el entorno de desarrollo del sistema.

read -p "Esta seguro que desea montar el ambiente de desarrollo? Presione S o s para continuar, cualquier otra tecla para finalizar la instalacion" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
fi
#Verificacion de las dependencias necesarias para psycopg2
dpkg -l | cut -d " " -f 3 | grep -q "^python3-dev" || \
 { echo "Se requiere la libreria python3-dev para continuar" ; exit 1; }
dpkg -l | cut -d " " -f 3 | grep -q "^libpq-dev" || \
 { echo "Se requiere la libreria libpq-dev para continuar" ; exit 1; }

#Variables
SCRIPT_PATH=$(pwd)
POSTGRES_USER="postgres"
POSTGRES_PASS="p0stgre5q1"
DB_NAME="proyecto_is2_dev"
DB_USER="proyecto_user_test"
DB_PASS="Pr0yect0Test"
DB_HOST="localhost"
DB_PORT="5432"
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
EMAIL_USE_TLS="True"
GIT_URL="https://github.com/marzeperez99/proyecto_is2.git"
TAG="iteracion_3"
GDRIVE_JSON_PATH="proyecto_is2/settings/credenciales/gdriveaccess.json"
ENV_VARIABLES_PATH="proyecto_is2/settings/credenciales/.env"

#Lectura de los datos de la Base de datos
read -rp "Ingrese el nombre de la Base de datos usado por el sistema [$DB_NAME]: " input
DB_NAME=${input:-$DB_NAME}
read -p "Ingrese el usuario de PostgreSQL [$POSTGRES_USER]: " input
POSTGRES_USER=${input:-$POSTGRES_USER}
read -p "Ingrese la contraseña del usuario de PostgreSQL [$POSTGRES_PASS]: " input
POSTGRES_PASS=${input:-$POSTGRES_PASS}

# Datos de la Base de Datos
read -rp "Ingrese el usuario a crear de PostgreSQL usado por el sistema [$DB_USER]: " input
DB_USER=${input:-$DB_USER}
read -rp "Ingrese la contraseña del usuario a crear utilizado por el sistema [$DB_PASS]: " input
DB_PASS=${input:-$DB_PASS}

GOOGLE_OAUTH_SECRET_KEY=""
read -rp "Ingrese el SECRET KEY del servicio de Google OAuth [$GOOGLE_OAUTH_SECRET_KEY]: " input
GOOGLE_OAUTH_SECRET_KEY=${input:-$GOOGLE_OAUTH_SECRET_KEY}
GOOGLE_OAUTH_CLIENT_ID=""
read -rp "Ingrese el CLIENT ID del servicio de Google OAuth [$GOOGLE_OAUTH_CLIENT_ID]: " input
GOOGLE_OAUTH_CLIENT_ID=${input:-$GOOGLE_OAUTH_CLIENT_ID}

# Variables del correo electronico
echo "Ingrese el correo electronico de Gmail con el Sistema enviará los correos electronicos"
read $EMAIL_HOST_USER
echo "Ingrese la contraseña de la cuenta de Gmail"
read -s $EMAIL_HOST_PASSWORD

#Obtencion del codigo del repositorio remoto
git clone $GIT_URL --quiet
echo "Proyecto clonado"
cd proyecto_is2 || exit 1
read -p "Ingrese el tag que desea cargar [$TAG]: " input
TAG=${input:-$TAG}
# Se accede al tag correspondiente
git checkout tags/"$TAG" -b "$TAG"


# Seteo de variables de entorno
echo "
DB_USUARIO=\"$DB_USER\"
DB_NOMBRE=\"$DB_NAME\"
DB_PASSWORD=\"$DB_PASS\"
DB_HOST=\"$DB_HOST\"
DB_PORT=\"$DB_PORT\"
STATIC_ROOT=\"$BASE_DIR/$PROYECT_NAME/site/public/static/\"
DEBUG_VALUE=False
SECRET_KEY=\"$SECRET_KEY\"
MEDIA_ROOT=\"$PROYECT_NAME/media/\"
MEDIA_URL=\"$PROYECT_NAME/media/items/\"
CELERY_BROKER_URL=\"redis://localhost\"
EMAIL_HOST_USER=\"$EMAIL_HOST_USER\"
EMAIL_HOST_PASSWORD=\"$EMAIL_HOST_PASSWORD\"
EMAIL_USE_TLS=\"$EMAIL_USE_TLS\"
" | sudo tee "$ENV_VARIABLES_PATH" > /dev/null;

echo "- Variables de entorno seteadas"

#Creacion de nueva base de datos
scripts/build_database.sh "$DB_NAME" "$POSTGRES_USER" "$POSTGRES_PASS" "$DB_USER" "$DB_PASS"

export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings
pipenv run pipenv install > /dev/null
echo "- Dependencias instaladas"
pipenv run python manage.py migrate > /dev/null
echo "- Migraciones aplicadas"
# Carga de Datos
TEMP_DIR=$(mktemp -d)
SSO_KEYS="$TEMP_DIR/google_keys.json"
scripts/data/sso_config.sh "$GOOGLE_OAUTH_CLIENT_ID" "$GOOGLE_OAUTH_SECRET_KEY" > "$SSO_KEYS"
echo "- SSO configurado"
pipenv run python manage.py loaddata "$SSO_KEYS" > /dev/null
echo "- Datos cargados"
#pipenv run python manage.py shell < "scripts/create_admin.py" > /dev/null
pipenv run python manage.py loaddata "$SCRIPT_PATH/data.json"
scripts/run_server.sh -d
