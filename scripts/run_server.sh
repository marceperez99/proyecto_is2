#!/bin/bash
#Script que ejecuta el servidor
python --version
while getopts pdt: flag
	do
	    case "${flag}" in
	        p)
	          export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.prod_settings;
	          pip install -r "requirements.txt";
	          python manage.py migrate
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
            if [ $PYTEST_RESULT -eq 0 ] || [ $PYTEST_RESULT -eq 5 ]; then
              sudo service apache2 restart
            else
              echo "ALERTA: Existen pruebas unitarias que fallaron"
            fi
	          ;;
	        d)
	          export DJANGO_SETTINGS_MODULE=proyecto_is2.settings.dev_settings;
	          # Generacion del Entorno Virtual
            pipenv run pipenv install
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
            if [ $? -eq 0 ] || [ $? -eq 5 ]; then
              pipenv run python manage.py runserver
            else
                echo "No se pasaron todas las pruebas unitarias"
            fi
	          ;;
	        t)
            git checkout tags/"${OPTARG}" -b "${OPTARG}";
	          ;;
	        *) echo "Especifique -p configuraciones de Produccion, -d configuraciones de desarrollo";;
	    esac
	done
