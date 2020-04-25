#!/bin/bash
#Script encargado de crear la base de datos del entorno de Desarrollo
#Argumentos:
#$1 Nombre de la Base de Datos a crear
#$2 Nombre del usuario de Postgres a usar para crear la base de datos
#$3 Contraseña del usuario de Postgres a usar para crear la base de datos
#$4 Usuario para acceso a BD a crear para uso del Sistema
#$5 Contraseña del usuario de acceso a la BD usado por el sistema
DB_NAME=$1
POSTGRES_USER=$2
POSTGRES_PASS=$3
DB_USER=$4
DB_PASS=$5
echo $DB_NAME $POSTGRES_USER $POSTGRES_PASS $DB_USER $DB_PASS
#Creacion de nueva base de datos
echo "Base de Datos"
if echo "$POSTGRES_PASS" | sudo su - $POSTGRES_USER -c "psql -lqt | cut -d \| -f 1 | grep -w $DB_NAME"; then
  echo "Base de datos creada"
else
  echo "$POSTGRES_PASS" | sudo su - $POSTGRES_USER -c "psql -c 'CREATE DATABASE $DB_NAME'"
fi

#Creacion de Usuario para acceso a la base de datos
echo "Usuario"
if echo "$POSTGRES_PASS" | sudo su - $POSTGRES_USER -c "psql -t -c '\du' | cut -d \| -f 1 | grep -w $DB_USER  "; then
  echo "Usuario a crear ya existe"
else
  echo "$POSTGRES_PASS" | sudo -u $POSTGRES_USER psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASS'"
  echo "$POSTGRES_PASS" | sudo su - $POSTGRES_USER -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER';"
  echo "$POSTGRES_PASS" | sudo su - $POSTGRES_USER -c "psql -c 'ALTER USER $DB_USER CREATEDB';"
fi