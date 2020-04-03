from gestion_de_proyecto.models import *
from roles_de_sistema.models import *
from roles_de_proyecto.models import *
from gestion_de_tipo_de_item.models import *
from gestion_de_fase.models import *
from django.contrib.auth.models import User
from django.utils import timezone

# Creacion de Rol de Sistema Administrador


Proyecto.objects.all().delete()
Fase.objects.all().delete()
TipoDeItem.objects.all().delete()

# Usuario 1 y 2 tienen que ser gerentes de proyecto
user_1 = User.objects.get(pk=2)
user_2 = User.objects.get(pk=3)

p1 = Proyecto()
p1.nombre = "Proyecto de Ingenieria de Software"
p1.descripcion = "Sistema administrador de items de proyectos.\nContempla la creación de proyectos, la definición de sus fases, creación de tipos de items e items de proyecto."
p1.creador = user_1
p1.fecha_creacion = timezone.now()
p1.estado = "En Configuración"
p1.gerente = user_1
p1.save()
Comite.objects.create(proyecto=p1)
Participante.objects.create(proyecto=p1, usuario=user_1)

p2 = Proyecto()
p2.nombre = "Chatiin"
p2.descripcion = "Sistema de mensajeria movil que utiliza el modelo cliente servidor."
p2.creador = user_2
p2.fecha_creacion = timezone.now()
p2.estado = "En Configuración"
p2.gerente = user_2
p2.save()
Comite.objects.create(proyecto=p2)
Participante.objects.create(proyecto=p2, usuario=user_2)

p3 = Proyecto()
p3.nombre = "Collapsar"
p3.descripcion = "Sistema de transferencia de archivos entre computadoras conectadas por una red local por medio del " \
                 "sistema de portapapeles de linux. "
p3.creador = user_1
p3.fecha_creacion = timezone.now()
p3.estado = "En Configuración"
p3.gerente = user_1
p3.save()
Comite.objects.create(proyecto=p3)
Participante.objects.create(proyecto=p3, usuario=user_1)

f1 = Fase()
f1.fase_cerrada = False
f1.puede_cerrarse = False
f1.nombre = "Análisis de Requerimientos"
f1.proyecto = p1
f1.fase_anterior = None
f1.save()

f2 = Fase()
f2.fase_cerrada = False
f2.puede_cerrarse = False
f2.nombre = "Diseño y Arquitectura"
f2.proyecto = p1
f2.fase_anterior = f1
f2.save()

f3 = Fase()
f3.fase_cerrada = False
f3.puede_cerrarse = False
f3.nombre = "Implementación"
f3.proyecto = p1
f3.fase_anterior = f2
f3.save()

f4 = Fase()
f4.fase_cerrada = False
f4.puede_cerrarse = False
f4.nombre = "Pruebas"
f4.proyecto = p1
f4.fase_anterior = f3
f4.save()

f5 = Fase()
f5.fase_cerrada = False
f5.puede_cerrarse = False
f5.nombre = "Mantenimiento"
f5.proyecto = p1
f5.fase_anterior = f4
f5.save()

f6 = Fase()
f6.fase_cerrada = False
f6.puede_cerrarse = False
f6.nombre = "Planificación"
f6.proyecto = p3
f6.fase_anterior = None
f6.save()

f7 = Fase()
f7.fase_cerrada = False
f7.puede_cerrarse = False
f7.nombre = "Diseño"
f7.proyecto = p3
f7.fase_anterior = f6
f7.save()

f8 = Fase()
f8.fase_cerrada = False
f8.puede_cerrarse = False
f8.nombre = "Codificación"
f8.proyecto = p3
f8.fase_anterior = f7
f8.save()

f9 = Fase()
f9.fase_cerrada = False
f9.puede_cerrarse = False
f9.nombre = "Pruebas"
f9.proyecto = p3
f9.fase_anterior = f8
f9.save()

f10 = Fase()
f10.fase_cerrada = False
f10.puede_cerrarse = False
f10.nombre = "Diseño"
f10.proyecto = p2
f10.fase_anterior = None
f10.save()

f11 = Fase()
f11.fase_cerrada = False
f11.puede_cerrarse = False
f11.nombre = "Back-End"
f11.proyecto = p2
f11.fase_anterior = f10
f11.save()

f12 = Fase()
f12.fase_cerrada = False
f12.puede_cerrarse = False
f12.nombre = "Front-End"
f12.proyecto = p2
f12.fase_anterior = f11
f12.save()

f13 = Fase()
f13.fase_cerrada = False
f13.puede_cerrarse = False
f13.nombre = "Pruebas"
f13.proyecto = p2
f13.fase_anterior = f12
f13.save()

t1 = TipoDeItem()
t1.nombre = "Requerimiento Funcional"
t1.descripcion = "Especificación de un requerimiento funcional."
t1.prefijo = "RF"
t1.creador = user_1
t1.fase = f1
t1.fecha_creacion = timezone.now()
t1.save()

t2 = TipoDeItem()
t2.nombre = "Requerimiento No Funcional"
t2.descripcion = "Especificación de un requerimiento no funcional."
t2.prefijo = "RNF"
t2.creador = user_1
t2.fase = f1
t2.fecha_creacion = timezone.now()
t2.save()

t3 = TipoDeItem()
t3.nombre = "Caso de Uso"
t3.descripcion = "Especificación de un caso de uso del sistema."
t3.prefijo = "CU"
t3.creador = user_2
t3.fase = f2
t3.fecha_creacion = timezone.now()
t3.save()

abin = AtributoBinario()
abin.requerido = False
abin.max_tamaño = 5
abin.nombre = "Diagrama del caso de uso"
abin.tipo_de_item = t3
abin.save()

acad = AtributoCadena()
acad.nombre = "Descripción"
acad.requerido = True
acad.max_longitud = 400
acad.tipo_de_item = t1
acad.save()

acad = AtributoCadena()
acad.nombre = "Descripción"
acad.requerido = True
acad.max_longitud = 400
acad.tipo_de_item = t2
acad.save()
