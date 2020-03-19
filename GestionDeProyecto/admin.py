from django.contrib import admin

from GestionDeProyecto.models import Proyecto

# Register your models here.


class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion", "creador", "fechaCreacion", "estado")
    search_fields = ("creador", "fechaCreacion", "estado")
    list_filter = ("fechaCreacion", "estado")
    date_hierarchy = "fechaCreacion"


admin.site.register(Proyecto, ProyectoAdmin)
