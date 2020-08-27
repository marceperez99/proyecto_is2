#!/bin/bash
BASE_DIR=$1
PROYECT_NAME=$2
GIT_URL="https://github.com/marzeperez99/proyecto_is2.git"

git pull origin master

cd "$BASE_DIR/$PROYECT_NAME/django/$PROYECT_NAME/" || exit 1
# Crea directorios necesarios para el proyecto
echo "requirements.txt"
# Instalacion de dependencias
python -m pip install -r "requirements.txt"
python -m pip freeze
#Generacion de SECRET_KEY
SECRET_KEY=$(openssl rand -base64 32)
export SECRET_KEY

export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings
#Creacion de migraciones
python manage.py migrate

echo "Configuracion de SSO"
python manage.py shell < scripts/sso_setup.py
echo "Creacion de Rol de Sistema Administrador"
python manage.py shell < scripts/create_admin.py

#TODO: Carga de Datos en el sistema
#Generacion de documentacion automatica
cd docs
make html
cd ..

#Se juntan los archivos estaticos
python manage.py collectstatic

#Ejecucion de pruebas unitarias
pytest
PYTEST_RESULT=$?
#Ejecucion del servidor
if [ $PYTEST_RESULT -eq 0 ] || [ $PYTEST_RESULT -eq 5 ]; then
  sudo service apache2 restart
else
  echo "ALERTA: Existen pruebas unitarias que fallaron"
fi