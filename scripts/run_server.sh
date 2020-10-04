#!/bin/bash
#Script que ejecuta el servidor
python --version
while getopts pdt: flag
	do
	    case "${flag}" in
	        p)
	          export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings;
	          pip install -r "requirements.txt" > /dev/null;
	          python manage.py migrate > /dev/null;
	          # Se genera la documentacion.
	          cd docs || exit 1;
	          sudo mkdir build
	          sudo chmod ugo+rw build
            make html;
            cd ..;
            #Se juntan los archivos estaticos
            python manage.py collectstatic

            #Ejecucion de pruebas unitarias
            pytest
            PYTEST_RESULT=$?
            #Ejecucion del servidor
            sudo service apache2 restart
            echo "- Servidor Apache reiniciado"
            celery -A proyecto_is2 worker -l info
	          ;;
	        d)
	          export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings;
	          # Generacion del Entorno Virtual
            pipenv run pipenv install > /dev/null;
            pipenv run pipenv clean
            #Generacion de documentacion automatica
            cd docs || exit 1;
            pipenv run make html
            cd ..
            #Creacion de migraciones
            pipenv run python manage.py migrate
            #Ejecucion de pruebas unitarias
            pipenv run pytest
            #Ejecucion del servidor
            pipenv run celery -A proyecto_is2 worker -l info &
            pipenv run python manage.py runserver

	          ;;
	        t)
            git checkout tags/"${OPTARG}" -b "${OPTARG}";
	          ;;
	        *) echo "Especifique -p configuraciones de Produccion, -d configuraciones de desarrollo";;
	    esac
	done
