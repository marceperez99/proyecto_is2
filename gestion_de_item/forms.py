from django import forms
from django.db.models import Q
from gestion_de_item.models import VersionItem, Item


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
        self.fields['relacion'] = forms.ModelChoiceField(queryset=Item.objects.filter(
            Q(tipo_de_item__fase=self.tipo_de_item.fase) | Q(tipo_de_item__fase=self.tipo_de_item.fase.fase_anterior)))

        # Si es la primera fase no es obligatorio introducir una relación.
        if self.tipo_de_item.fase.fase_anterior is None:
            self.fields['relacion'].required = False

        self.fields['relacion'].empty_label = 'Seleccionar el antecesor/padre de este item'
        self.fields['relacion'].label = 'Antecesor/Padre'

        # Un codigo oculto para completar
        # self.fields['codigo'] = forms.CharField()
        # self.fields['codigo'].required = False
        # self.fields['codigo'].widget = forms.HiddenInput()

    # def clean_codigo(self):
    #   codigo = self.tipo_de_item.prefijo + '_' + str(self.tipo_de_item.item_set.all().count() + 1)
    #  return codigo
