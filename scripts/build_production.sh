#!/bin/bash
#Script que monta el ambiente de produccion del sistema

#Verificacion de las dependencias de apache
dpkg -l | cut -d " " -f 3 | grep -q "^apache2" || \
 { echo "Se requiere la libreria python3-dev para continuar" ; exit 1; }
dpkg -l | cut -d " " -f 3 | grep -q "^libapache2-mod-wsgi-py3" || \
 { echo "Se requiere la libreria libpq-dev para continuar" ; exit 1; }

#Confirmacion de que se desea continuar
echo "---¿Esta seguro que desea montar el ambiente de produccion?---
      Este script sobreescribira el 000-default.conf de apache2.
Presione Enter para continuar, Ctrl+C para finalizar la instalacion"
read -r
#VARIABLES
#SCRIPT_PATH=$(dirname "$0")
POSTGRES_USER="postgres"
POSTGRES_PASS="p0stgre5q1"
DB_NAME="proyecto_is2"
DB_USER="proyecto_admin"
DB_PASS="Pr0yect0Adm1n"
DB_HOST="localhost"
DB_PORT="5432"
PROYECT_NAME="proyecto_is2"
BASE_DIR="/var/www"
APACHE_DIR="/etc/apache2/sites-available"
GIT_URL="https://github.com/marzeperez99/proyecto_is2.git"

GDRIVE_JSON_PATH="$BASE_DIR/$PROYECT_NAME/auth/gdriveaccess.json"

echo "El sistema se instalará en la carpeta $BASE_DIR"
##Lectura de los datos de la Base de datos
read -rp "Ingrese el usuario de PostgreSQL [$POSTGRES_USER]: " input
POSTGRES_USER=${input:-$POSTGRES_USER}
read -rp "Ingrese la contraseña del usuario de PostgreSQL [$POSTGRES_PASS]: " input
POSTGRES_PASS=${input:-$POSTGRES_PASS}

ENV_VARIABLES_PATH="$BASE_DIR/$PROYECT_NAME/auth/.env"
# Lectura de variables de entorno del proyecto
read -rp "Ingrese el nombre de la Base de datos usado por el sistema [$DB_NAME]: " input
DB_NAME=${input:-$DB_NAME}
read -rp "Ingrese el usuario de PostgreSQL usado por el sistema [$DB_USER]: " input
DB_USER=${input:-$DB_USER}
read -rp "Ingrese la contraseña del usuario utilizado por PostgreSQL [$DB_PASS]: " input
DB_PASS=${input:-$DB_PASS}
read -rp "Ingrese direccion del servicio PostgreSQL [$DB_HOST]: " input
DB_HOST=${input:-$DB_HOST}
read -rp "Ingrese el puerto del servicio PostgreSQL [$DB_PORT]: " input
DB_PORT=${input:-$DB_PORT}
# Lectura de variables de entorno de SSO
GOOGLE_OAUTH_SECRET_KEY="k8WE0-Oeon0FnGDAo03X5IQo"
read -rp "Ingrese el SECRET KEY del servicio de Google OAuth [$GOOGLE_OAUTH_SECRET_KEY]: " input
GOOGLE_OAUTH_SECRET_KEY=${input:-$GOOGLE_OAUTH_SECRET_KEY}
GOOGLE_OAUTH_CLIENT_ID="628176483267-fu449k587f887bm7n5tgc8alndtb35t1.apps.googleusercontent.com"
read -rp "Ingrese el CLIENT ID del servicio de Google OAuth [$GOOGLE_OAUTH_CLIENT_ID]: " input
GOOGLE_OAUTH_CLIENT_ID=${input:-$GOOGLE_OAUTH_CLIENT_ID}

GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=" ../proyecto_is2/settings/gdriveaccess.json"
read -rp "Ingrese la ruta del archivo el contenido de las credenciales proveidas para el uso de la plataforma de Google Drive [$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE]: " input
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=${input:-$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE}
echo "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE"
if [ ! -f "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE" ]; then
  echo "Archivo de credenciales no existente"
  exit 1
fi
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=$(cat "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE")

cd "$BASE_DIR" || exit 1

##Creacion de directorios del sistema
sudo mkdir -p "$PROYECT_NAME"/{site/{logs,public},django,auth,media}
sudo chmod -R ugo+rwx "$PROYECT_NAME/site/public"

echo "- Directorios necesarios creados"


cd $PROYECT_NAME || exit 1
##Creacion y activacion del entorno virtual
sudo virtualenv venv -p python3 > /dev/null
sudo chmod -R ugo+rwx venv || exit 1
source venv/bin/activate > /dev/null
echo "- Entorno virtual creado"
#
SECRET_KEY=$(openssl rand -base64 32)
##Creacion de variables de entorno
echo "
DB_USUARIO=\"$DB_USER\"
DB_NOMBRE=\"$DB_NAME\"
DB_PASSWORD=\"$DB_PASS\"
DB_HOST=\"$DB_HOST\"
DB_PORT=\"$DB_PORT\"
GOOGLE_OAUTH_SECRET_KEY=\"$GOOGLE_OAUTH_SECRET_KEY\"
GOOGLE_OAUTH_CLIENT_ID=\"$GOOGLE_OAUTH_CLIENT_ID\"
STATIC_ROOT=\"$BASE_DIR/$PROYECT_NAME/site/public/static/\"
DEBUG_VALUE=False
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=\"$GDRIVE_JSON_PATH\"
SECRET_KEY=\"$SECRET_KEY\"
MEDIA_ROOT=\"$PROYECT_NAME/media\"
" | sudo tee "$ENV_VARIABLES_PATH" > /dev/null;

echo "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE" | sudo tee "$GDRIVE_JSON_PATH" > /dev/null;
echo "- Variables de Entorno guardadas";

#Descarga de codigo fuente
cd "django" || exit 1
sudo git clone $GIT_URL --quiet || exit 1
echo "Repositorio clonado"
cd "$PROYECT_NAME" || exit 1

# Se obtiene el tag a cargar
TAG='iteracion_3'
read -rp "Ingrese el nombre tag que desea montar [$TAG]: " input
TAG=${input:-$TAG}

sudo git checkout tags/"$TAG" -b "$TAG"

# Se configura apache
read -p "Se sobreescribira el archvivo 000-default.conf de apache2 para incluir configuraciones del Sistema. Presione S para continuar, cualquier otra tecla para finalizar la instalacion" -n 1 -r
#echo
if [[  $REPLY =~ ^[Ss]$ ]]; then
    scripts/data/apache_config.sh "$BASE_DIR" > "$APACHE_DIR"/000-default.conf
fi

# Se configura la Base de Datos
scripts/build_database.sh "$DB_NAME" "$POSTGRES_USER" "$POSTGRES_PASS" "$DB_USER" "$DB_PASS"
echo "- Base de Datos creada"

export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings
# Se instalan dependencias
pip install -r "requirements.txt" > /dev/null;
# Se corren migraciones de Django
python manage.py migrate
# Se cargan datos

scripts/load_data.sh  "$GOOGLE_OAUTH_CLIENT_ID" "$GOOGLE_OAUTH_SECRET_KEY"

cd scripts || exit 1
# Se corre el servidor
export VENV_PATH="/var/www/proyecto_is2/venv/bin/activate"
./run_server.sh -p;