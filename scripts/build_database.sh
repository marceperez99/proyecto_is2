#!/bin/bash
DB=$1
USER=$2
PASS=$3
#Creacion de nueva base de datos
if echo "$PASS" | sudo su - $USER -c "psql -lqt | cut -d \| -f 1 | grep -w $DB"; then
  echo "Base de datos creada"
else
  echo "$PASS" | sudo su - $USER -c "psql -c 'CREATE DATABASE $DB'"
fi