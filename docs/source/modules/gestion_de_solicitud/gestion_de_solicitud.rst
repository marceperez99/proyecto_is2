.. index:: Solicitudes

Solicitudes
*************
Modulo encargado del manejo de las solicitudes del sistema.

Una vez creada una linea base en una fase esta puede ser solicitada para su ruptura, para la modificacion de los item
que se encuentren dentro de ella. Esta accion solo podra ser efectuada por un usuario con los permisos de solicitar
ruptura de linea base. En la solicitud se deberan especificar las siguientes cosas
    -Descripcion: se escribira el motivo por el cual se quiere romper la linea base
    -Cambios necesarios: seleccionar los item que quieres que se modifique.

Se debe analizar previamente el impacto que generara la modificacion de los item selecionados, se debe presentar ya con
una solucion factible el cambio, puesto que este sera analizado por el comite de cambio para ver si es factible o no este.

Una vez generada y enviada la solicitud esta es analizada por el comite de cambio, estos votan a fovor o en contra como
les parezca, una vez todos hayan votado puede pasar dos cosas:

    1- Que la solicitud haya sido aprobada, lo que implica lo siguiente:
        -La linea base queda en estodo rota (se rompe la linea base)
        -Los item seleccionados para su modificacion psan al estado "A Modificar"
        -Los item que no fueron seleccionados para su modificacion pasan al estado "En Revicion", estos item son sometidos
            a verificacion, donde se verifica si es que necesitan algun cambio. Si no necesitan cambio, pasan al estado
            anteriror, de lo contrario pasan al estado "A Modificar"

    2- Que la solicitud haya sido rechazada, lo que implica lo siguiente:
        -Ningun cambio en la linea base


Modelos
==========
.. automodule:: gestion_de_solicitud.models
    :members:

Vistas
=========
.. automodule:: gestion_de_solicitud.views
    :members:

Pruebas Unitarias
==================
.. automodule:: gestion_de_solicitud.tests.tests
    :members:
