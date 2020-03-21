from django import forms

from gestion_de_proyecto.models import Participante


class NuevoParticipanteForm(forms.ModelForm):

    class Meta:
        model = Participante
        fields = ['usuario', 'rol']


class SeleccionarPermisosForm(forms.Form):

    def __init__(self, proyecto, rol, *args, **kwargs):
        super(SeleccionarPermisosForm, self).__init__(*args,**kwargs)
        for fase in proyecto.get_fases():
            print([(pp.codename, pp.name) for pp in rol.get_permisos()])
            self.fields[f'f_{fase.id}'] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                choices=[(pp.codename, pp.name) for pp in rol.get_pp_por_fase()],
                label=f'Fase {fase.nombre}'
            )
