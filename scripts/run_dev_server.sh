#!/bin/bash
#Inicia el servidor con las configuraciones de desarrollo
export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings

# Generacion del Entorno Virtual
pipenv run pipenv install
pipenv run pipenv clean

#Generacion de documentacion automatica
pwd
cd docs
pipenv run make html
cd ..
#Creacion de migraciones
pipenv run python manage.py migrate
#Creacion de Rol de Sistema Administrador
pipenv run python manage.py shell < scripts/create_admin.py
#TODO: Descomentar linea de abajo cuando se tenga un archivo data.json bien hecho
# pipenv run python manage.py loaddata data.json
#Ejecucion de pruebas unitarias
pipenv run pytest
#Ejecucion del servidor
if [ $? -eq 0 -o $? -eq 5 ]; then
  pipenv run python manage.py runserver
else
    echo "No se pasaron todas las pruebas unitarias"
fi
