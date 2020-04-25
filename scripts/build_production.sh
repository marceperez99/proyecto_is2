#!/bin/bash
#Script que monta el ambiente de produccion del sistema

#Verificacion de las dependencias de apache
dpkg -l | cut -d " " -f 3 | grep -q "^apache2" || \
 { echo "Se requiere la libreria python3-dev para continuar" ; exit 1; }
dpkg -l | cut -d " " -f 3 | grep -q "^libapache2-mod-wsgi-py3" || \
 { echo "Se requiere la libreria libpq-dev para continuar" ; exit 1; }

#Confirmacion de que se desea continuar
read -p "Esta seguro que desea montar el ambiente de produccion? Este script sobreescribira el 000-default.conf de apache2. Presione S para continuar, cualquier otra tecla para finalizar la instalacion" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
fi

#VARIABLES
SCRIPT_PATH=$(dirname $0)
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

# Se lee donde se ubicara el proyecto
read -p "Ingrese el directorio donde se colocará el Sistema [$BASE_DIR]: " input
BASE_DIR=${input:-$BASE_DIR}

#Lectura de los datos de la Base de datos
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
GOOGLE_OAUTH_SECREY_KEY=""
read -p "Ingrese el SECRET KEY del servicio de Google OAuth [$GOOGLE_OAUTH_SECREY_KEY]: " input
GOOGLE_OAUTH_SECREY_KEY=${input:-$GOOGLE_OAUTH_SECREY_KEY}
GOOGLE_OAUTH_CLIENT_ID=""
read -p "Ingrese el SECRET KEY del servicio de Google OAuth [$GOOGLE_OAUTH_CLIENT_ID]: " input
GOOGLE_OAUTH_CLIENT_ID=${input:-$GOOGLE_OAUTH_CLIENT_ID}

cd "$BASE_DIR" || exit 1

#Creacion de directorios del sistema
mkdir -p "$PROYECT_NAME"/{site/{logs,public},django,auth}

#creacion del entorno virtual
cd $PROYECT_NAME || exit 1


#Creacion y activacion del entorno virtual
virtualenv venv -p python3
source venv/bin/activate
python --version

#Creacion de variables de entorno
{ echo "DB_USUARIO=\"$DB_USER\"";
echo "DB_NOMBRE=\"$DB_NAME\"" ;
echo "DB_PASSWORD=\"$DB_PASS\"" ;
echo "DB_HOST=\"$DB_HOST\"";
echo "DB_PORT=\"$DB_PORT\"";
echo "GOOGLE_OAUTH_SECREY_KEY=\"$GOOGLE_OAUTH_SECREY_KEY\"";
echo "GOOGLE_OAUTH_CLIENT_ID=\"$GOOGLE_OAUTH_CLIENT_ID\"" ;
echo "STATIC_ROOT=\"$BASE_DIR/$PROYECT_NAME/site/public/static/\"" ;
echo "DEBUG_VALUE=False"; } > "$ENV_VARIABLES_PATH"

#Descarga de codigo fuente
cd "django" || exit 1
git clone $GIT_URL
cd "$PROYECT_NAME" || exit 1


read -p "Se sobreescribira el archvivo 000-default.conf de apache2 para incluir configuraciones del Sistema. Presione S para continuar, cualquier otra tecla para finalizar la instalacion" -n 1 -r
echo
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
    " > $APACHE_DIR/000-default.conf
fi


scripts/build_database.sh "$DB_NAME" "$POSTGRES_USER" "$POSTGRES_PASS" "$DB_USER" "$DB_PASS"
source scripts/run_prod_server.sh "$BASE_DIR" "$PROYECT_NAME"