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
SCRIPT_PATH=$(dirname $0)
POSTGRES_USER="postgres"
POSTGRES_PASS="p0stgre5q1"
DB_NAME="proyecto_is2_dev"
DB_USER="proyecto_user_test"
DB_PASS="Pr0yect0Test"
GIT_URL="https://github.com/marzeperez99/proyecto_is2.git"
TAG="iteracion_3"
GDRIVE_JSON_PATH="proyecto_is2/settings/credenciales/gdriveaccess.json"

#Lectura de los datos de la Base de datos
read -p "Ingrese el usuario de PostgreSQL [$POSTGRES_USER]: " input
POSTGRES_USER=${input:-$POSTGRES_USER}
read -p "Ingrese la contraseña del usuario de PostgreSQL [$POSTGRES_PASS]: " input
POSTGRES_PASS=${input:-$POSTGRES_PASS}

GOOGLE_OAUTH_SECRET_KEY=""
read -rp "Ingrese el SECRET KEY del servicio de Google OAuth [$GOOGLE_OAUTH_SECRET_KEY]: " input
GOOGLE_OAUTH_SECRET_KEY=${input:-$GOOGLE_OAUTH_SECRET_KEY}
GOOGLE_OAUTH_CLIENT_ID=""
read -rp "Ingrese el CLIENT ID del servicio de Google OAuth [$GOOGLE_OAUTH_CLIENT_ID]: " input
GOOGLE_OAUTH_CLIENT_ID=${input:-$GOOGLE_OAUTH_CLIENT_ID}

GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=gdriveaccess.json
read -rp "Ingrese la ruta del archivo el contenido de las credenciales proveidas para el uso de la plataforma de Google Drive [$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE]: " input
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=${input:-$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE}
echo "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE"
if [ ! -f "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE" ]; then
  echo "Archivo de credenciales no existente"
  exit 1
fi
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=$(cat "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE")


#Obtencion del codigo del repositorio remoto
git clone $GIT_URL --quiet
echo "Proyecto clonado"
cd proyecto_is2 || exit 1
read -p "Ingrese el tag que desea cargar [$TAG]: " input
TAG=${input:-$TAG}
# Se accede al tag correspondiente
git checkout tags/"$TAG" -b "$TAG"

# Se guarda las credenciales de Google Drive
mkdir "proyecto_is2/settings/credenciales" || exit 1
echo "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE" > "$GDRIVE_JSON_PATH"
echo "Credenciales de Google Drive guardadas"
#Creacion de nueva base de datos
scripts/build_database.sh "$DB_NAME" "$POSTGRES_USER" "$POSTGRES_PASS" "$DB_USER" "$DB_PASS"

export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings
pipenv run pipenv install > /dev/null
echo "Dependencias instaladas"
pipenv run python manage.py migrate > /dev/null
echo "Migraciones aplicadas"
# Carga de Datos
TEMP_DIR=$(mktemp -d)
SSO_KEYS="$TEMP_DIR/google_keys.json"
scripts/data/sso_config.sh "$GOOGLE_OAUTH_CLIENT_ID" "$GOOGLE_OAUTH_SECRET_KEY" > "$SSO_KEYS"
echo "SSO configurado"
pipenv run python manage.py loaddata "$SSO_KEYS" > /dev/null
echo "Datos cargados"
pipenv run python manage.py shell < "scripts/create_admin.py" > /dev/null
#pipenv run python manage.py loaddata data.json
scripts/run_server.sh -d
