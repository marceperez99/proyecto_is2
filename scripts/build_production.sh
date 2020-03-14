#!/bin/bash
#Script que monta todo el ambiente de produccion del sistema

read -p "Esta seguro que desea montar el ambiente de produccion? Este script sobreescribira el 000-default.conf de apache2. Presione S para continuar, cualquier otra tecla para finalizar la instalacion" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
fi

#Creacion de directorios
PROYECT_NAME="proyecto_is2"
BASE_DIR="/var/www"
GIT_URL="https://github.com/marzeperez99/proyecto_is2.git"
APACHE_DIR="/etc/apache2/sites-available"
cd $BASE_DIR

#Creacion de directorios del sistema
mkdir -p $PROYECT_NAME/{site/{logs,public},django,auth}
#creacion del entorno virtual
cd $PROYECT_NAME
#Creacion y activacion del entorno virtual
virtualenv venv -p python3

#Descarga de codigo fuente
#TODO: desmarcar cuando se haya enviado todo a git el codigo
#git clone $GIT_URL

echo $BASE_DIR/$PROYECT_NAME/django/$PROYECT_NAME/requirements.txt
#TODO: desmarcar cuando este todo configurado
#pip install -r $BASE_DIR/$PROYECT_NAME/django/$PROYECT_NAME/requirements.txt


#cat $BASE_DIR/$PROYECT_NAME/django/$PROYECT_NAME/scripts/apache.conf > $APACHE_DIR/000-default.conf
