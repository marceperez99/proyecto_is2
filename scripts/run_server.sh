#!/bin/bash
#Script que ejecuta el servidor
python --version
while getopts pdt: flag
	do
	    case "${flag}" in
	        p)
	          pip install -r "requirements.txt" > /dev/null;
	          DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings python manage.py migrate > /dev/null;
	          # Se genera la documentacion.
	          cd docs || exit 1;
	          sudo mkdir build
	          sudo chmod ugo+rw build
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings make html;
            cd ..;
            #Se juntan los archivos estaticos
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings python manage.py collectstatic

            #Ejecucion de pruebas unitarias
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings pytest
            PYTEST_RESULT=$?
            #Ejecucion del servidor
            sudo service apache2 restart
            echo "- Servidor Apache reiniciado"
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings celery -A proyecto_is2 worker -l info

	          ;;
	        d)
	          # Generacion del Entorno Virtual
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings pipenv run pipenv install > /dev/null;
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings pipenv run pipenv clean
            #Generacion de documentacion automatica
            cd docs || exit 1;
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings pipenv run make html
            cd ..
            #Creacion de migraciones
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings pipenv run python manage.py migrate
            #Ejecucion de pruebas unitarias
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings pipenv run pytest
            #Ejecucion del servidor
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings pipenv run celery -A proyecto_is2 worker -l info &
            DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings pipenv run python manage.py runserver

	          ;;
	        *) echo "Especifique -p configuraciones de Produccion, -d configuraciones de desarrollo";;
	    esac
	done
