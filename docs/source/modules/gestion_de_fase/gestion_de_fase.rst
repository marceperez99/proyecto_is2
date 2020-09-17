.. index:: Fases

Fases
*******************
Módulo encargado de la administración de las Fases dentro de un Proyecto.

Dentro de las Fases se pueden definir tipos de items, que actúan como plantillas para la creación
de ítems dentro de la Fase, se puede crear, modificar, eliminar, aprobar ítems. Se puede crear
Líneas Base para crear un conjunto de ítems de la fase que ya no sufrirán modificaciones.

El sistema permite la creación de fases dentro de un proyecto en Configuración, para esto
el gerente del proyecto deberá proporcionar un nombre para la Fase, una descripción y la fase
tras la cual se posicionará la nueva fase, esto permite que se puedan ir agregando fases
entre las fases ya creadas.

Las fases pueden ser cerradas, esto hace que dentro de la fase cerrada ya no puedan realizarse ningun
tipo de cambio. Para poder cerrar una fase se debe cumplir que:

    - Todos los items deben estar en una Linea Base Cerrada.
    - Todos los items deben ser trazables a la siguiente fase o pertenecer a la ultima fase.

Las fases pueden ser modificadas o eliminadas siempre y cuando el proyecto se encuentre en Configuración.



Vistas
=========
.. automodule:: gestion_de_fase.views
    :members:

Modelos
==========
.. automodule:: gestion_de_fase.models
    :members:

Pruebas unitarias
==========================
.. automodule:: gestion_de_fase.tests.tests
    :members:
