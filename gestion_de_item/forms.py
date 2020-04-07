from django import forms
from django.db.models import Q
from gestion_de_item.models import VersionItem, Item, EstadoDeItem


class NuevoVersionItemForm(forms.ModelForm):
    class Meta:
        model = VersionItem
        fields = ['nombre', 'descripcion', 'peso']

    def __init__(self, *args,tipo_de_item=None, item=None, **kwargs):
        super(NuevoVersionItemForm, self).__init__(*args, **kwargs)

        self.tipo_de_item = tipo_de_item
        self.item = item
        # Consigue todos los items de la fase actual o anterior.
        # LEE LA ERS
        queryset = Item.objects.filter(Q(tipo_de_item__fase=self.tipo_de_item.fase) & (Q(estado=EstadoDeItem.APROBADO) | Q(estado=EstadoDeItem.EN_LINEA_BASE) )| Q(tipo_de_item__fase=self.tipo_de_item.fase.fase_anterior) & Q(estado=EstadoDeItem.EN_LINEA_BASE))
        self.fields['relacion'] = forms.ModelChoiceField(queryset = queryset)

        # Si es la primera fase no es obligatorio introducir una relación.
        if self.tipo_de_item.fase.fase_anterior is None:
            self.fields['relacion'].required = False

        self.fields['relacion'].empty_label = 'Seleccionar el antecesor/padre de este item'
        self.fields['relacion'].label = 'Antecesor/Padre'


