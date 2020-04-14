from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from gestion_de_item.models import VersionItem, Item, EstadoDeItem, AtributoItemArchivo, AtributoItemCadena, \
    AtributoItemNumerico, AtributoItemBooleano, AtributoItemFecha
#from gestion_de_item.utils import hay_ciclo
import gestion_de_item

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


class EditarItemForm(forms.ModelForm):
    class Meta:
        model = VersionItem
        fields = ['nombre', 'descripcion', 'peso']


class AtributoItemArchivoForm(forms.Form):

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        super(AtributoItemArchivoForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.FileField()
        self.fields[self.nombre].empty_label = 'Seleccionar un archivo'
        self.fields[self.nombre].label = plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido

    def clean(self):
        # Falta validar el tamaño maximo del archivo

        return self.cleaned_data


class AtributoItemCadenaForm(forms.Form):

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        super(AtributoItemCadenaForm, self).__init__(*args, **kwargs)

        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.CharField()
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido

    def clean(self):
        valor = self.cleaned_data[self.nombre]
        if len(valor) > self.plantilla.max_longitud:
            raise ValidationError('La longitud del texto supera la longitud permitida por el tipo de item')
        return self.cleaned_data


class AtributoItemNumericoForm(forms.Form):

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        super(AtributoItemNumericoForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.DecimalField(max_digits=plantilla.max_digitos,
                                                      decimal_places=plantilla.max_decimales)
        print(plantilla.max_digitos)
        print(plantilla.max_decimales)
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido


class AtributoItemBooleanoForm(forms.Form):

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        super(AtributoItemBooleanoForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.BooleanField()
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs["format"] = "%d-%m-%Y"
        super().__init__(**kwargs)


class AtributoItemFechaForm(forms.Form):

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        super(AtributoItemFechaForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.DateField()
        #self.fields[self.nombre] = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.DateInput(format='%d-%m-%y'))
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido
        self.fields[self.nombre].widget = DateInput() #Este es un widget creado mas arriba



class RelacionPadreHijoForm(forms.Form):

    def __init__(self, *args, item=None, **kwargs):
        super(RelacionPadreHijoForm, self).__init__(*args, **kwargs)
        self.fields['padre'] = forms.ModelChoiceField(queryset=item.get_fase().get_item_estado(EstadoDeItem.APROBADO))
        self.item = item

    def clean_padre(self):
        padre = self.cleaned_data['padre']
        hijo = self.item
        if gestion_de_item.utils.hay_ciclo(padre, hijo):
            raise ValidationError('La relacion no se puede formar, pues va a formar una dependencia ciclica')
        else:
            return padre
