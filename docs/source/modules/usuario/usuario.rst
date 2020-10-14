.. index:: Usuarios

Usuarios
*******************
Módulo de Administración de los usuarios del Sistema.

Los usuarios van se registran y se autentican en el sistema mediante el uso de el servicio
de autenticacion de Google.

A cada usuario del sistema se le va asignando un rol de Sistema que le permitirá acceder
al sistema y, dependiendo si el rol asignado cuenta con permisos especiales, podrá acceder
a información como a la lista de usuarios, lista de roles de sistema o de proyectos.

La primera vez que el usuario ingresa al sistema este no podrá ingresar al mismo, en ese
momento se notifica a los administradores del sistema del nuevo acceso, una vez asignado
el rol el usuario podrá entrar con normalidad al sistema.

Vistas
=========
.. automodule:: usuario.views
    :members:

Modelos
==========
.. automodule:: usuario.models
    :members:

Pruebas Unitarias
=======================
.. automodule:: usuario.tests.tests
    :members: