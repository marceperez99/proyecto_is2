from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from gestion_de_item.models import VersionItem, Item, EstadoDeItem, AtributoItemArchivo, AtributoItemCadena, \
    AtributoItemNumerico, AtributoItemBooleano, AtributoItemFecha


class NuevoVersionItemForm(forms.ModelForm):
    class Meta:
        model = VersionItem
        fields = ['nombre', 'descripcion', 'peso']

    def __init__(self, *args, tipo_de_item=None, item=None, **kwargs):
        super(NuevoVersionItemForm, self).__init__(*args, **kwargs)

        self.tipo_de_item = tipo_de_item
        self.item = item
        # Consigue todos los items de la fase actual o anterior.
        # LEE LA ERS
        queryset = Item.objects.filter(Q(tipo_de_item__fase=self.tipo_de_item.fase) & (
                Q(estado=EstadoDeItem.APROBADO) | Q(estado=EstadoDeItem.EN_LINEA_BASE)) | Q(
            tipo_de_item__fase=self.tipo_de_item.fase.fase_anterior) & Q(estado=EstadoDeItem.EN_LINEA_BASE))
        self.fields['relacion'] = forms.ModelChoiceField(queryset=queryset)

        # Si es la primera fase no es obligatorio introducir una relación.
        if self.tipo_de_item.fase.fase_anterior is None:
            self.fields['relacion'].required = False

        self.fields['relacion'].empty_label = 'Seleccionar el antecesor/padre de este item'
        self.fields['relacion'].label = 'Antecesor/Padre'


class AtributoItemArchivoForm(forms.ModelForm):
    class Meta:
        model = AtributoItemArchivo
        fields = ['url']
        widgets = {'url': forms.HiddenInput}

    def __init__(self, *args, plantilla=None, **kwargs):
        super(AtributoItemArchivoForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.fields['archivo'] = forms.FileField()
        self.fields['archivo'].empty_label = 'Seleccionar un archivo'
        self.fields['archivo'].label = 'Archivo'
        self.fields['archivo'].required = self.plantilla.requerido
        self.fields['url'].required = False
    def clean_archivo(self):
        # Falta validar el tamaño maximo del archivo
        archivo = self.cleaned_data['archivo']
        return archivo


class AtributoItemCadenaForm(forms.ModelForm):
    class Meta:
        model = AtributoItemCadena
        fields = ['valor']

    def __init__(self, *args, plantilla=None, **kwargs):
        super(AtributoItemCadenaForm, self).__init__(*args, **kwargs)

        self.plantilla = plantilla
        self.fields['valor'].label = self.plantilla.nombre
        self.fields['valor'].required = self.plantilla.requerido

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if len(valor) > self.plantilla.max_longitud:
            raise ValidationError('La longitud del texto supera la longitud permitida por el tipo de item')
        return valor


class AtributoItemNumericoForm(forms.ModelForm):
    class Meta:
        model = AtributoItemNumerico
        fields = ['valor']

    def __init__(self, *args, plantilla=None, **kwargs):
        super(AtributoItemNumericoForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.fields['valor'].label = self.plantilla.nombre
        self.fields['valor'].required = self.plantilla.requerido

    def clean_valor(self):
        valor = int(self.cleaned_data['valor'])
        if len(valor) > self.plantilla.max_digitos:
            raise ValidationError(
                'La cantidad de digitos no decimales  supera la cantidad permitida por el tipo de item')
        return valor


class AtributoItemBooleanoForm(forms.ModelForm):
    class Meta:
        model = AtributoItemBooleano
        fields = ['valor']

    def __init__(self, *args, plantilla=None, **kwargs):
        super(AtributoItemBooleanoForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.fields['valor'].label = self.plantilla.nombre
        self.fields['valor'].required = self.plantilla.requerido

class DateInput(forms.DateInput):
    input_type = 'date'
class AtributoItemFechaForm(forms.ModelForm):
    class Meta:
        model = AtributoItemFecha
        fields = ['valor']
        widgets = {'valor': DateInput()}


    def __init__(self, *args, plantilla=None, **kwargs):
        super(AtributoItemFechaForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        #self.fields['valor'] = forms.DateField()
        self.fields['valor'].label = self.plantilla.nombre
        self.fields['valor'].required = self.plantilla.requerido
