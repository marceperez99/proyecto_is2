.. index:: Roles de Sistema

Roles de Sistema
*******************
Módulo del sistema que se encarga de la gestión de los roles de sistema.

Un rol de sistema es un conjunto de permisos de sistema que pueden ser asignados a un usuario.

Cada rol de sistema esta conformado por un nombre, una descripćión y el conjunto de permisos que contempla.

El usuario administrador del sistema tiene por defecto todos los permisos de sistema.

Los roles de sistema pueden ser editados y eliminados siempre que no exista ningún usuario con ese rol asignado.

Vistas
=========
.. automodule:: roles_de_sistema.views
    :members:

Modelos
==========
.. automodule:: roles_de_sistema.models
    :members:

Pruebas unitarias
==========================
.. automodule:: roles_de_sistema.tests.tests
    :members:
