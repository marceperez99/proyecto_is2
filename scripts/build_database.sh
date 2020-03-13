#!/bin/bash
DB=$1
USER=$2
PASS=$3
#Creacion de nueva base de datos
echo "$PASS" | sudo su - $USER -c "psql -c 'CREATE DATABASE $DB'"