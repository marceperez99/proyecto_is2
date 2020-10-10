BASE_DIR=$1;
echo "
      <VirtualHost *:80>
	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/proyecto_is2

	ErrorLog /var/www/proyecto_is2/site/logs/error.log
	CustomLog /var/www/proyecto_is2/site/logs/access.log combined

	alias /static /var/www/proyecto_is2/site/public/static

	<Directory /var/www/proyecto_is2>
		Require host localhost
  		Require ip 127.0.0.1
  		Require ip 192.168
  		Require ip 10
	</Directory>

	<Directory /var/www/proyecto_is2/site/public/static>
		Require all granted
	</Directory>

	<Directory /var/www/proyecto_is2/django/proyecto_is2/proyecto_is2>
		<Files wsgi.py>
			Require all granted
		</Files>
	</Directory>
	WSGIDaemonProcess proyecto_is2 python-path=/var/www/proyecto_is2/django/proyecto_is2/ python-home=/var/www/proyecto_is2/venv
	WSGIProcessGroup proyecto_is2
	WSGIScriptAlias / /var/www/proyecto_is2/django/proyecto_is2/proyecto_is2/wsgi.py
</VirtualHost>
"