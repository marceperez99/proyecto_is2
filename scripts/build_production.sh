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
SCRIPT_PATH=$(dirname "$0")
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
read -p "Ingrese el usuario de PostgreSQL [$POSTGRES_USER]: " input
POSTGRES_USER=${input:-$POSTGRES_USER}
read -p "Ingrese la contraseña del usuario de PostgreSQL [$POSTGRES_PASS]: " input
POSTGRES_PASS=${input:-$POSTGRES_PASS}

ENV_VARIABLES_PATH="$BASE_DIR/$PROYECT_NAME/auth/.env"
# Lectura de variables de entorno del proyecto
read -p "Ingrese el nombre de la Base de datos usado por el sistema [$DB_NAME]: " input
DB_NAME=${input:-$DB_NAME}
read -p "Ingrese el usuario de PostgreSQL usado por el sistema [$DB_USER]: " input
DB_USER=${input:-$DB_USER}
read -p "Ingrese la contraseña del usuario utilizado por PostgreSQL [$DB_PASS]: " input
DB_PASS=${input:-$DB_PASS}
read -p "Ingrese direccion del servicio PostgreSQL [$DB_HOST]: " input
DB_HOST=${input:-$DB_HOST}
read -p "Ingrese el puerto del servicio PostgreSQL [$DB_PORT]: " input
DB_PORT=${input:-$DB_PORT}
# Lectura de variables de entorno de SSO
GOOGLE_OAUTH_SECRET_KEY=""
read -p "Ingrese el SECRET KEY del servicio de Google OAuth [$GOOGLE_OAUTH_SECRET_KEY]: " input
GOOGLE_OAUTH_SECRET_KEY=${input:-$GOOGLE_OAUTH_SECRET_KEY}
GOOGLE_OAUTH_CLIENT_ID=""
read -p "Ingrese el CLIENT ID del servicio de Google OAuth [$GOOGLE_OAUTH_CLIENT_ID]: " input
GOOGLE_OAUTH_CLIENT_ID=${input:-$GOOGLE_OAUTH_CLIENT_ID}

GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE="apache_config.txt"
read -p "Ingrese la ruta del archivo el contenido de las credenciales proveidas para el uso de la plataforma de Google Drive [$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE]: " input
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=${input:-$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE}

if [ ! -f "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE" ]; then
  echo "Archivo de credenciales no existente"
  exit 1
fi
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=$(cat "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE")

cd "$BASE_DIR" || exit 1

##Creacion de directorios del sistema
sudo mkdir -p "$PROYECT_NAME"/{site/{logs,public},django,auth,media}
echo "- Directorios necesarios creados"
#
##creacion del entorno virtual
cd $PROYECT_NAME || exit 1
#
#
##Creacion y activacion del entorno virtual
virtualenv venv -p python3 > /dev/null 2>&1
source venv/bin/activate
python --version
#
SECRET_KEY=$(openssl rand -base64 32)
##Creacion de variables de entorno
{ echo "DB_USUARIO=\"$DB_USER\"";
echo "DB_NOMBRE=\"$DB_NAME\"" ;
echo "DB_PASSWORD=\"$DB_PASS\"" ;
echo "DB_HOST=\"$DB_HOST\"";
echo "DB_PORT=\"$DB_PORT\"";
echo "GOOGLE_OAUTH_SECRET_KEY=\"$GOOGLE_OAUTH_SECRET_KEY\"";
echo "GOOGLE_OAUTH_CLIENT_ID=\"$GOOGLE_OAUTH_CLIENT_ID\"" ;
echo "STATIC_ROOT=\"$BASE_DIR/$PROYECT_NAME/site/public/static/\"" ;
echo "DEBUG_VALUE=False";
echo "GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE=\"$GDRIVE_JSON_PATH\"";
echo "SECRET_KEY=\"$SECRET_KEY\"";
echo "MEDIA_ROOT=\"$PROYECT_NAME/media\"";} > "$ENV_VARIABLES_PATH";
echo "$GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE" > "$GDRIVE_JSON_PATH";
echo "Guardando Variables de Entorno";

##Descarga de codigo fuente
cd "django" || exit 1
git clone $GIT_URL --quiet
echo "Repositorio clonado"
cd "$PROYECT_NAME" || exit 1
TAG='iteracion_3'
read -p "Ingrese el nombre tag que desea montar [$TAG]: " input
TAG=${input:-$TAG}

git checkout tags/"$TAG" -b "$TAG"


read -p "Se sobreescribira el archvivo 000-default.conf de apache2 para incluir configuraciones del Sistema. Presione S para continuar, cualquier otra tecla para finalizar la instalacion" -n 1 -r
#echo
if [[  $REPLY =~ ^[Ss]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && echo "
      <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot $BASE_DIR/html

        ErrorLog $BASE_DIR/proyecto_is2/site/logs/error.log
        CustomLog $BASE_DIR/proyecto_is2/site/logs/access.log combined

        alias /static $BASE_DIR/proyecto_is2/site/public/static
        <Directory $BASE_DIR/proyecto_is2/site/public/static>
          Require all granted
        </Directory>

        <Directory $BASE_DIR/proyecto_is2/django/proyecto_is2/proyecto_is2>
          <Files wsgi.py>
            Require all granted
          </Files>
        </Directory>
        WSGIDaemonProcess proyecto_is2 python-path=$BASE_DIR/proyecto_is2/django/proyecto_is2/ python-home=$BASE_DIR/proyecto_is2/venv
        WSGIProcessGroup proyecto_is2
        WSGIScriptAlias / $BASE_DIR/proyecto_is2/django/proyecto_is2/proyecto_is2/wsgi.py
      </VirtualHost>
    " > "$APACHE_DIR"/000-default.conf
fi


scripts/build_database.sh "$DB_NAME" "$POSTGRES_USER" "$POSTGRES_PASS" "$DB_USER" "$DB_PASS"
source scripts/run_prod_server.sh "$BASE_DIR" "$PROYECT_NAME"