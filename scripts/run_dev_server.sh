#!/bin/bash
#Inicia el servidor con las configuraciones de desarrollo
export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings

export DB_NAME="proyecto_is2_dev"
export DB_USER="postgres"
export DB_PASS="p0stgre5q1"

#Generacion de Base de datos de prueba
./scripts/build_database.sh $DB_NAME $DB_USER $DB_PASS


#Generacion de documentacion automatica
#TODO: colocar compando de sphinx

#Creacion de migraciones
python manage.py makemigrations
python manage.py migrate

#Ejecucion de pruebas unitarias
pytest
#Ejecucion del servidor
if [ $? -eq 0 -o $? -eq 5 ]; then
  python manage.py runserver
fi
