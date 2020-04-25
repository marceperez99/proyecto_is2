#!/bin/bash
BASE_DIR=$1
PROYECT_NAME=$2
GIT_URL="https://github.com/marzeperez99/proyecto_is2.git"

# Crea directorios necesarios para el proyecto
echo "$BASE_DIR/$PROYECT_NAME/django/$PROYECT_NAME/requirements.txt"
# Instalacion de dependencias
python -m pip install -r "$BASE_DIR/$PROYECT_NAME/django/$PROYECT_NAME/requirements.txt"
python -m pip freeze
#Generacion de SECRET_KEY
export SECRET_KEY=$(openssl rand -base64 32)


export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings
#Creacion de migraciones
python manage.py makemigrations
python manage.py migrate

#Generacion de documentacion automatica
cd docs
make html
cd ..

#Ejecucion de pruebas unitarias
pytest
PYTEST_RESULT=$?
#Ejecucion del servidor
if [ $PYTEST_RESULT -eq 0 ] || [ $PYTEST_RESULT -eq 5 ]; then
  sudo service apache2 restart
fi