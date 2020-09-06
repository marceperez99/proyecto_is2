BASE_DIR=$1;
echo "
      <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot $BASE_DIR/html

        ErrorLog $BASE_DIR/proyecto_is2/site/logs/error.log
        CustomLog $BASE_DIR/proyecto_is2/site/logs/access.log combined

        alias /static $BASE_DIR/proyecto_is2/site/public/static
        <Directory $BASE_DIR/proyecto_is2/site/public/static>
          Require all granted
        </Directory>

        <Directory $BASE_DIR/proyecto_is2/django/proyecto_is2/proyecto_is2>
          <Files wsgi.py>
            Require all granted
          </Files>
        </Directory>
        WSGIDaemonProcess proyecto_is2 python-path=$BASE_DIR/proyecto_is2/django/proyecto_is2/ python-home=$BASE_DIR/proyecto_is2/venv
        WSGIProcessGroup proyecto_is2
        WSGIScriptAlias / $BASE_DIR/proyecto_is2/django/proyecto_is2/proyecto_is2/wsgi.py
      </VirtualHost>
    "