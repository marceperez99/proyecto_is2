from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from gestion_de_item.models import VersionItem, Item, EstadoDeItem, AtributoItemArchivo, AtributoItemCadena, \
    AtributoItemNumerico, AtributoItemBooleano, AtributoItemFecha
# from gestion_de_item.utils import hay_ciclo
import gestion_de_item


class NuevoVersionItemForm(forms.ModelForm):
    """
    Form que permite la creación de un nuevo item. Solicita los atributos no dinamicos del item.
    Es necesario especificar un padre o un sucesor para el nuevo item si es que no se encuentra en la primera fase del proyecto.


    Campos:
        - nombre: str, nombre del nuevo ítem.
        - descripción: str, descripción del nuevo ítem.
        - peso: int, peso del nuevo ítem.
        - Antecesor/Padre: Item, padre o antecesor de este item (no requerido en la primera fase)
    """
    descripcion = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))

    class Meta:
        model = VersionItem
        fields = ['nombre', 'descripcion', 'peso']

    def __init__(self, *args, tipo_de_item=None, **kwargs):
        """
        Constructor de la clase NuevoVersionItemForm.
        Los items candidatos para el campo Antecesor/Padre son seleccionados de la fase anterior aquellos que estan en una linea base y de la fase actual si estan aprobados o en linea base.

        Argumentos:
            - tipo_de_item: TipoDeITem, el tipo de item al quen pertenece este item.

        """
        super(NuevoVersionItemForm, self).__init__(*args, **kwargs)

        self.tipo_de_item = tipo_de_item
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
    """
    Form que permite editar los atributos no dinamicos del item.

    Campos:
        -nombre: str, nombre del item
        -descripción: str, descripción del item.
        -peso: int, peso del item.
    """

    class Meta:
        model = VersionItem
        fields = ['nombre', 'descripcion', 'peso']


class AtributoItemArchivoForm(forms.Form):
    """
    Form que permite crear y editar atributos dinamicos del tipo 'Archivo'.

    Campos:
        - File

    """

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        """
        Constructor del form AtributoItemArchivoForm.

        Argumentos:
            - plantilla: AtributoArchivo

        """
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
    """
    Form que permite crear y editar atributos dinamicos del tipo 'Cadena'.

    Validaciones:
        - La longitud del texto no debe superar la especificada en la plantilla del atributo.

    Campos:
        - str

    """

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        """
        Constructor del form AtributoItemCadenaForm.


        Argumentos:
            - plantilla: AtributoCadena
        """

        super(AtributoItemCadenaForm, self).__init__(*args, **kwargs)

        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.CharField()
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido

    def clean(self):
        """
        Método que valida que la longitud de la cadena no supere la especificada en la plantilla del atributo.

        """
        valor = self.cleaned_data[self.nombre]
        if len(valor) > self.plantilla.max_longitud:
            raise ValidationError('La longitud del texto supera la longitud permitida por el tipo de item')
        return self.cleaned_data


class AtributoItemNumericoForm(forms.Form):
    """
       Form que permite crear y editar atributos dinamicos del tipo 'Numerico'.

       Validaciones:
           - La cantidad total de digitos del número no puede superar la especificada en la plantilla del atributo.
           - La cantidad de digitos decimales no puede superar la especificada en la plantilla del atributo.
       Campos:
           - Decimal

    """

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        """
        Constructor del form AtributoItemNumericoForm.

        Argumentos:
            - plantilla: AtributoNumerico

        """
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
    """
    Form que permite crear y editar atributos dinamicos del tipo 'Booleano'.

    Campos:
        - boolean

    """

    def __init__(self, *args, plantilla=None, counter=None, **kwargs):
        """
        Constructor del form AtributoItemBooleanoForm.

        Argumentos:
            - plantilla: AtributoBooleano

        """

        marcado = False
        if 'initial' in kwargs:
            marcado = kwargs['initial']['valor_' + str(counter)]
        super(AtributoItemBooleanoForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked': marcado}))
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = False


class AtributoItemFechaForm(forms.Form):
    """

    Form que permite crear y editar atributos dinamicos del tipo 'Fecha'.

    Campos:
        - Date
    """

    def __init__(self, *args, plantilla=None, fecha=None, counter=None, **kwargs):
        """
        Constructor del form AtributoItemFechaForm.

        Argumentos:
            - plantilla: AtributoFecha
        """
        print(fecha, counter)
        super(AtributoItemFechaForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.DateField()
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido
        self.fields[self.nombre].widget = forms.DateInput(attrs={'type': 'date', 'value': fecha})


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


class RelacionAntecesorSucesorForm(forms.Form):

    def __init__(self, *args, item=None, **kwargs):
        super(RelacionAntecesorSucesorForm, self).__init__(*args, **kwargs)
        self.fields['antecesor'] = forms.ModelChoiceField(
            queryset=item.get_fase().fase_anterior.get_item_estado(EstadoDeItem.EN_LINEA_BASE))
        self.item = item

    #    def clean_antecesor(self):
     #   antecesor = self.cleaned_data['antecesor']
      #  sucesor = self.item
       # if gestion_de_item.utils.hay_ciclo(antecesor, sucesor):
        #    raise ValidationError('La relacion no se puede formar, pues va a formar una dependencia ciclica')
       # else:
         #   return antecesor
