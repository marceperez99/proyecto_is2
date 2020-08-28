from django import forms

from gestion_de_fase.models import Fase
from gestion_de_item.models import Item
from gestion_de_proyecto.models import Participante, Proyecto


class AsignacionForm(forms.Form):
    modificar = forms.BooleanField(required=False)

    usuario = forms.ModelChoiceField(label='Asignar a', queryset=Participante.objects.all(), required=False)

    motivo = forms.CharField(label='comentario', max_length=500, required=False)

    def __init__(self, *args, proyecto_id, fase_id, **kwargs):
        super(AsignacionForm, self).__init__(*args, **kwargs)
        self.proyecto_id = proyecto_id
        proyecto = Proyecto.objects.get(id=proyecto_id)
        fase = Fase.objects.get(id=fase_id)
        self.fields["usuario"].queryset = Participante.objects.all().filter(proyecto=proyecto)
        con_permiso = list(
            map(lambda x: x.id,
                filter(lambda x: proyecto.tiene_permiso_de_proyecto_en_fase(x.usuario, fase, "pp_f_modificar_item"),
                       self.fields["usuario"].queryset)))
        self.fields["usuario"].queryset = Participante.objects.all().filter(pk__in=con_permiso)

        # TODO: Conseguir los participantes con permiso de modificar (?


class SolicitudForm(forms.Form):
    razon_rompimiento = forms.CharField(label='Descripción del motivo de rompimiento', widget=forms.Textarea())
