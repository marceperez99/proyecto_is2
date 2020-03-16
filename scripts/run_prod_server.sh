#!/bin/bash

DB_NAME="proyecto_is2"
DB_USER="postgres"
DB_PASS="p0stgre5q1"


DIR=$1
#
cd $DIR

source ../../venv/bin/activate
pip install -r requirements.txt
#Generacion de SECRET_KEY
export SECRET_KEY=$(openssl rand -base64 32)

#Generacion de la base de datos
./scripts/build_database.sh $DB_NAME $DB_USER $DB_PASS

export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings
#Creacion de migraciones
python manage.py makemigrations
python manage.py migrate

#Generacion de documentacion automatica
#TODO: incluir comando de sphinx

#Ejecucion de pruebas unitarias
pytest
#Ejecucion del servidor
if [ $? -eq 0 -o $? -eq 5 ]; then
  sudo service apache2 restart
fi