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

#Obtencion del codigo del repositorio remoto
git clone $GIT_URL
cd proyecto_is2 || exit 1
read -p "Ingrese el tag que desea cargar [$TAG]: " input
TAG=${input:-$TAG}
# Se accede al tag correspondiente
git checkout tags/"$TAG" -b "$TAG"

#Lectura de los datos de la Base de datos
read -p "Ingrese el usuario de PostgreSQL [$POSTGRES_USER]: " input
POSTGRES_USER=${input:-$POSTGRES_USER}
read -p "Ingrese la contraseña del usuario de PostgreSQL [$POSTGRES_PASS]: " input
POSTGRES_PASS=${input:-$POSTGRES_PASS}

#Creacion de nueva base de datos
scripts/build_database.sh "$DB_NAME" "$POSTGRES_USER" "$POSTGRES_PASS" "$DB_USER" "$DB_PASS"
scripts/run_dev_server.sh

