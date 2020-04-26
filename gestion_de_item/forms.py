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

        self.fields[self.nombre].required = self.plantilla.requerido and 'initial' not in kwargs.keys()

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
        super(AtributoItemFechaForm, self).__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.nombre = 'valor_' + str(counter)
        self.fields[self.nombre] = forms.DateField()
        self.fields[self.nombre].label = self.plantilla.nombre
        self.fields[self.nombre].required = self.plantilla.requerido
        self.fields[self.nombre].widget = forms.DateInput(attrs={'type': 'date', 'value': fecha})


class RelacionPadreHijoForm(forms.Form):
    """
    Form que permite la creación de un nueva relacion padre-hijo entre item.
    Es necesario especificar un padre para el item.\n
    Campos:
        -padre: Item, futuro padre del item selecionado
    """

    def __init__(self, *args, item=None, **kwargs):
        """
        Constructor de la clase RelacionPadreHijoForm.
        Los items candidatos para el campo Padre son seleccionados de la misma fase y que estan aprobados.

        Argumentos:
            - item: Item, items que esten estado aprobado

        """
        super(RelacionPadreHijoForm, self).__init__(*args, **kwargs)
        self.fields['padre'] = forms.ModelChoiceField(queryset=item.get_fase().get_item_estado(EstadoDeItem.APROBADO, EstadoDeItem.EN_LINEA_BASE).exclude(id=item.id))
        self.item = item

    def clean_padre(self):
        """
        Método que verifica que la nueva relacion no forme un ciclo, con la ayuda de la funcion "hay_ciclo".
        Saltara un mensaje de error en caso de que forme algun ciclo.
        Retorna:
            True: si la relacion no forma ciclo
        """
        padre = self.cleaned_data['padre']
        hijo = self.item
        if gestion_de_item.utils.hay_ciclo(padre, hijo):
            raise ValidationError('La relacion no se puede formar, pues va a formar una dependencia ciclica')
        else:
            return padre


class RelacionAntecesorSucesorForm(forms.Form):
    """
    Form que permite la creación de un nueva relacion antecesor-sucesor entre item.
    Es necesario especificar un antecesor para el item si es que no se encuentra en la primera fase del proyecto.


    Campos:
        - Antecesor: Item, antecesor de este item (no requerido en la primera fase)
    """

    def __init__(self, *args, item=None, **kwargs):
        """
        Constructor de la clase RelacionAntecesorSucesorForm.
        Los items candidatos para el campo Antecesor son seleccionados de la fase anterior aquellos que estan en una linea base.

        Argumentos:
            - item: Item, items de la fase anterior que cumplan que esten en una linea base

        """
        super(RelacionAntecesorSucesorForm, self).__init__(*args, **kwargs)
        self.fields['antecesor'] = forms.ModelChoiceField(
            queryset=item.get_fase().fase_anterior.get_item_estado(EstadoDeItem.EN_LINEA_BASE))
        self.item = item

