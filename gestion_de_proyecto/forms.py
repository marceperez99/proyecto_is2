from django import forms

from gestion_de_proyecto.models import Participante


class NuevoParticipanteForm(forms.ModelForm):
    usuario = forms.ChoiceField()

    class Meta:
        model = Participante
        fields = ['usuario', 'rol']


class SeleccionarPermisosForm(forms.Form):

    def __init__(self, usuario, proyecto, rol, *args, **kwargs):
        super(SeleccionarPermisosForm, self).__init__(*args, **kwargs)
        for fase in proyecto.get_fases():
            self.fields[f'f_{fase.id}'] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                choices=[(pp.codename, pp.name) for pp in rol.get_pp_por_fase()],
                label=f'Fase {fase.nombre}'
            )
            self.usuario = usuario
            self.permisos_de_proyecto = list(rol.get_pp_por_proyecto())
            self.rol = rol
