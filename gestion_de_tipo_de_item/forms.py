from django.forms import ModelForm
from .models import TipoDeItem, AtributoCadena, AtributoBooleano, AtributoFecha, AtributoNumerico, AtributoBinario


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


class AtributoCadenaForm(ModelForm):
    class Meta:
        model = AtributoCadena
        fields = ['nombre','requerido','max_longitud']
class AtributoArchivoForm(ModelForm):
    class Meta:
        model = AtributoBinario
        fields = ['nombre','requerido','max_tamaño']
class AtributoNumericoForm(ModelForm):
    class Meta:
        model = AtributoNumerico
        fields = ['nombre','requerido','max_digitos','max_decimales']
class AtributoFechaForm(ModelForm):
    class Meta:
        model = AtributoFecha
        fields = ['nombre','requerido']
class AtributoBooleanoForm(ModelForm):
    class Meta:
        model = AtributoBooleano
        fields = ['nombre','requerido']

