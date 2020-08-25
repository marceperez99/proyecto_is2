from django import forms

from gestion_de_item.models import Item
from gestion_de_proyecto.models import Participante


class AsignacionForm(forms.Form):
    modificar = forms.BooleanField(required=False)
    usuario = forms.ModelChoiceField(label='Asignar a', queryset=Participante.objects.all(), required=False)

    motivo = forms.CharField(label='comentario',max_length=200, required=False)


class SolicitudForm(forms.Form):
    razon_rompimiento = forms.CharField(label='Descripción del motivo de rompimiento',widget=forms.Textarea())
