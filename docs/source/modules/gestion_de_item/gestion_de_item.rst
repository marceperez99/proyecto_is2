.. index:: Ítems

Ítems
*************
Módulo encargado de la administración de los items pertenecientes a una fase.

Para crear un item se debe seleccionar una fase abierta del proyecto, se necesita un usuario con permisos de crear item,
al momento de la creacion se pedira seleccionar a que tipo de item pertenecera este, no esta permitido usar un Tipo de
Item de otra fase, tambien se deben rellenar los campos de Nombre, Descripcion, Peso y Antecesor/Padre. Para este ultimo
campo se deberan tener conseideraciones espaciales, se puede dejar en blanco solo si el item a crear va a pertencer a la
primera fase, para relacionar con un padre, el item padre tiene que estar Aprobado y en la mima fase del item que vamos
a crear, en el caso para relacionar con un antecesor este debera de estar en una Linea Base y en una fase adyacente
anterior.

A un item recien creado se le asignara el estado de "No Aprobado", en este estado se le pueden hacer modificaciones al
item, por cada modificaion realizada el item tendra una nueva version, teniendo la posibilidad de volver a una version
anteriror, siempre y cuando en esta version del item sea trazable a la primera fase.

Un item puede tener varios estados, en cada estado cumple una funcion en la fase, por lo que es importante saber como
pasar de un estado a otro y que se puede hacer con el en ese estado, veremos los estado de los item.

- No Aprobado:
    | Estado inicial de item cuando se crea, en este se pueden hacer modificaciones de sus atributos y relaciones.
    | El item puede volver a este estado si se encunetra en los estado de "Aprobado" o "A aprobar", y si no tiene
    | ninguna relacion de padre/hijo o de antecesor/sucesor con otro item.
    | En este estado el item pude vovlver a una version anterior, siempre que siga siendo trabable a la primera fase.

- Listo para su aprobación:
    | Cuando un item con el estado de "No Aprobado" se solicita para ser "Aprobado".
    | En este estado se comprueba que le item este todo en orden para pasar al esatdo "Aprobado".

- Aprobado:
    | Cuando se acepto la solicitud de aprobacion del item, ahora se encuentra con estado "Aprobado".
    | En este estado el item puede ser incluido en la ista de padres de otros item o ser incluido en una Linea Base.

- En Linea Base:
    | Cuando un item con estado Aprobado se le mete en una linea base, este pasa a tener el estado de "En Linea Base"
    | Se le puede poner en la lista de antecesores de un item con estado "No aprobado" o "A Modificar", de una fase
    | adyacente posterior.

- A modificar:
    | Cuando se acepta la solicitud de romper una linea base, los item seleccionados para su modificacion pasan al
    | estado "A modificar", se tiene que saber de ante mano las relaciones o atributos de los item con este estado que
    | se tienen que modificar.

- En Revisión:
    | Los item que no fueron seleccionados para su modificacion en el momento de romper una linea base se ponen en
    | estado "En revision", se tiene que comprobar si los item necesitan ser modificados, asi tambien los items que sean
    | sucesores o hijos directos de items que fueron afectados por una Ruptura de Linea Base pasarán a este estado.
    | Este estado es un estado de verificación, un usuario con permiso de verificar un item en revision deberá verificar
    | los datos del item y deberá terminar la revisión, una vez finalizada la revisión el item pasará a En Linea Base si
    | este pertenece a una linea base y en caso contrario pasará al estado Aprobado.
    | Si un item que estaba En Revision necesita un cambio, la responsabilidad de solicitar el cambio de este item recae
    | sobre el usuario, este deberá tomar las acciones necesarias para poder realizar una solicitud de Ruptura de Linea
    | Base para que el item pueda ser modificado.

- Eliminado:
    | Para eliminar un item de una fase este tiene que estar necesariamente en el estado "No Aprobado", su eliminacion
    | se hace de forma logica en el proyecto y no podra volver a ningun otro estado.

| La unica forma de comunicar items es a travez de sus relaciones, pero para poder hacerlas hay unas cuantas normas a tener
| en cuenta. Al crear una relacion entre dos items esta no debera formar un ciclo, ni podra relacionarse con un item con
| el cual ya tenga una relacion existente. Al momento de eliminar una relacion se verificara que siga siendo trabable a la
| primera fase y se creara una nueva version sin esa relacion.


Modelos
==========
.. automodule:: gestion_de_item.models
    :members:

Vistas
=========
.. automodule:: gestion_de_item.views
    :members:

Pruebas Unitarias
==================
.. automodule:: gestion_de_item.tests.tests
    :members:
