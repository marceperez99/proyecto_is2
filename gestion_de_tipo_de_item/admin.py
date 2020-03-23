from django.contrib import admin
from .models import TipoDeItem
from .models import AtributoBinario
from .models import AtributoBooleano
from .models import AtributoCadena
from .models import AtributoNumerico
from .models import AtributoFecha

# Register your models here.
admin.site.register(TipoDeItem)
admin.site.register(AtributoNumerico)
admin.site.register(AtributoCadena)
admin.site.register(AtributoBinario)
admin.site.register(AtributoFecha)
admin.site.register(AtributoBooleano)

