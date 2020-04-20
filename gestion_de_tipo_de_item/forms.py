from django import forms

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

    def __init__(self, *args, proyecto=None, tipo_de_item=None, **kwargs):
        super(TipoDeItemForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        self.tipo_de_item = tipo_de_item

    def clean_prefijo(self):
        prefijo = self.cleaned_data.get('prefijo')
        fases = self.proyecto.get_fases()
        for fase in fases:
            tipos = fase.tipodeitem_set.all()
            for tipo in tipos:
                if tipo.prefijo == prefijo and not self.tipo_de_item == tipo:
                    raise forms.ValidationError('El prefijo debe ser único dentro del proyecto')
        return prefijo


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
        fields = ['nombre']
