.. index:: Gestion de Proyecto

Proyectos
*******************

Módulo de encargado de la gestión de un proyecto.

Un proyecto es creado por un administrador del sistema, este le asigna al Proyecto un
usuario que tendrá el Rol de Proyecto Gerente.

Inicialmente el proyecto se encontrará en un estado donde el gerente del Proyecto deberá:

    - Asignar un Comite de Cambios compuesto por un número impar,mayor a 1, de participantes del proyecto.
    - Crear, Modificar y eliminar Fases dentro del Proyecto.
    - Agregar participantes y asignarles un Rol de Proyecto.
    - Definir, editar y eliminar tipos de item dentro de las fases creadas.

Una vez finalizada la etapa de Configuración, el gerente podrá iniciar el Proyecto, con lo que los participantes
de este podrán:

    - Crear items dentro de las fases.
    - Modificar items creados.
    - Eliminar items creados.
    - Solicitar Aprobación, Aprobar, Desaprobar items.
    - Definir, editar y eliminar tipos de item dentro de las fases creadas.
    - Crear Lineas Base.
    - Cerrar Fases.
    - Finalizar Proyecto.

Al finalizar el Proyecto solo se podrán visualizar los datos del Proyecto, ya no se podrá agregar, modificar
o eliminar nada.

Así tambien, el gerente del Proyecto puede Cancelar el proyecto, con lo que no se podrá hacer ningun cambio
al Proyecto, este solo podrá ser visualizado por usuarios con el permiso de sistema correspondiente.

Vistas
=========
.. automodule:: gestion_de_proyecto.views
    :members:

Modelos
==========
.. automodule:: gestion_de_proyecto.models
    :members:

Decoradores
============
.. automodule:: gestion_de_proyecto.decorators
    :members:

Pruebas Unitarias
==================
.. automodule:: gestion_de_proyecto.tests.tests
    :members: