from django.contrib import admin

# Register your models here.
from gestion_de_solicitud.models import SolicitudDeCambio, Asignacion

admin.site.register(SolicitudDeCambio)
admin.site.register(Asignacion)