.. index:: Roles de Proyecto

Roles de Proyecto
*******************
Módulo de encargado del manejo de los Roles de Proyecto.

Un rol de Proyecto es un conjunto de permisos de Proyecto que puede ser asignado a
un usuario dentro de un Proyecto.

Los permisos de Proyecto incluidos en un Rol de Proyecto son utilizados como base para asignar a
los participantes de un proyecto los permisos correspondientes, al momento de asignar un rol de
Proyecto, el sistema solicitará al usuario que esté asignando el rol a otro participante que
seleccione los permisos de proyecto que desea que se le asigne al participante por cada fase del
proyecto que se haya creado hasta el momento.

Los Roles de Proyecto pueden ser modificados y eliminados siempre y cuando ningún usuario tenga
asignado dicho Rol en algún Proyecto.

Vistas
=========
.. automodule:: roles_de_proyecto.views
    :members:

Modelos
==========
.. automodule:: roles_de_proyecto.models
    :members:

Pruebas Unitarias
==================
.. automodule:: roles_de_proyecto.tests
    :members: