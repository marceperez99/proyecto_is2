from django import forms
from django.forms import Form
from django.shortcuts import get_object_or_404

from gestion_de_fase.models import Fase
from .models import TipoDeItem, AtributoCadena, AtributoBooleano, AtributoFecha, AtributoNumerico, AtributoBinario


class TipoDeItemForm(forms.ModelForm):
    """
    nombre: string\n
        descripcion: string\n
        prefijo: string\n
        creador: User\n
        fase: Fase\n
        fecha_creacion: date\n


    """
    descripcion = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))

    class Meta:
        model = TipoDeItem
        fields = ['nombre', 'descripcion', 'prefijo']


class AtributoCadenaForm(forms.ModelForm):
    tipo = forms.CharField(widget=forms.HiddenInput, initial='cadena')

    class Meta:
        model = AtributoCadena
        fields = ['nombre', 'requerido', 'max_longitud']


class AtributoArchivoForm(forms.ModelForm):
    tipo = forms.CharField(widget=forms.HiddenInput, initial='archivo')

    class Meta:
        model = AtributoBinario
        fields = ['nombre', 'requerido', 'max_tamaño']


class AtributoNumericoForm(forms.ModelForm):
    tipo = forms.CharField(widget=forms.HiddenInput, initial='numerico')

    class Meta:
        model = AtributoNumerico
        fields = ['nombre', 'requerido', 'max_digitos', 'max_decimales']


class AtributoFechaForm(forms.ModelForm):
    tipo = forms.CharField(widget=forms.HiddenInput, initial='fecha')

    class Meta:
        model = AtributoFecha
        fields = ['nombre', 'requerido']


class AtributoBooleanoForm(forms.ModelForm):
    tipo = forms.CharField(widget=forms.HiddenInput, initial='booleano')

    class Meta:
        model = AtributoBooleano
        fields = ['nombre', 'requerido']


class ImportarTipoDeItemForm(forms.Form):

    def __init__(self, fase, *args, **kwargs):
        super(ImportarTipoDeItemForm, self).__init__()
        self.fase = fase
        self.tipo_de_items = forms.ModelChoiceField(TipoDeItem.objects.all().exclude(fase=self.fase), empty_label='Seleccione un tipo de item')
