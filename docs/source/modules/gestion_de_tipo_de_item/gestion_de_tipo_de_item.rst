.. index:: Gestión de tipo de item

Tipos de items
*******************
Módulo de gestión de tipos de items del sistema.

Un tipo de item es una plantilla para la creación de items dentro de las fases de un proyecto.
Cada tipo de item esta formado por un conjunto de atributos estáticos, compartidos por todos los items,
y un conjunto de atributos dinámicos, que el usuario puede agregar al tipo.

Los atributos estáticos son:

    - Nombre: nombre del tipo de item, máximo 100 caracteres.
    - Descripción: descripción del tipo de item, máximo 400 caracteres.
    - Prefijo: cadena de texto que será utilizada para crear el identificador de los items creados con el tipo de item
    - Creador: usuario que creó el tipo de item.
    - Fase: fase de un proyecto donde fue definido el tipo de item.

Los atributos dinámicos son definidos por el usuario al momento de crear el tipo de item y pueden ser:

    - Texto: al agregar este atributo se deberá especificar el nombre del campo, la longitud máxima y si el campo será requerido o no.
    - Numérico: se deberá especificar el nombre del campo, la cantidad maxima de digitos y decimales y si el campo será requerido o no.
    - Fecha: se deberá especificar el nombre del campo,y si el campo será requerido o no.
    - Booleano: se deberá especificar el nombre del campo.
    - Archivo: se deberá especificar el nombre del campo y el tamaño máximo del archivo.

Al momento de crear un tipo de item se podrá importar un tipo de item de otro proyecto del sistema o de otras fases
del mismo proyecto, al realizar esto el sistema mostrará la pantalla de creación de tipo de item con todos los atributos
del tipo a importar y permitirá la modificación de los campos de este.

Un tipo de item podrá ser modificado o eliminado siempre y cuando no exista un item creado con ese tipo de item.



Vistas
=========
.. automodule:: gestion_de_tipo_de_item.views
    :members:

Modelos
==========
.. automodule:: gestion_de_tipo_de_item.models
    :members:

Funciones utilitarias
=======================
.. automodule:: gestion_de_tipo_de_item.utils
    :members:

Pruebas Unitarias
=======================
.. automodule:: gestion_de_tipo_de_item.tests.tests
    :members:

