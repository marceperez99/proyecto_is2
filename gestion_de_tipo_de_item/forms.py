from django.forms import ModelForm
from .models import TipoDeItem


class TipoDeItemForm(ModelForm):
    """
    nombre: string\n
        descripcion: string\n
        prefijo: string\n
        creador: User\n
        fase: Fase\n
        fecha_creacion: date\n


    """

    class Meta:
        model = TipoDeItem
        fields = ['nombre', 'descripcion', 'prefijo']
