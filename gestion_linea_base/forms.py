from django import forms

from gestion_de_item.models import Item
from gestion_de_proyecto.models import Participante


class AsignacionForm(forms.Form):
    modificar = forms.BooleanField(required=False)

    usuario = forms.ModelChoiceField(label='Asignar a', queryset=Participante.objects.all(), required=False)

    motivo = forms.CharField(label='comentario', max_length=200, required=False)

    def __init__(self, *args, proyecto_id,item = None, **kwargs):
        super(AsignacionForm, self).__init__(*args, **kwargs)
        self.proyecto_id = proyecto_id
        self.item = item
        #TODO: Conseguir los participantes con permiso de modificar (?

class SolicitudForm(forms.Form):
    razon_rompimiento = forms.CharField(label='Descripción del motivo de rompimiento', widget=forms.Textarea())
