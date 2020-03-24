from django import forms
from gestion_de_fase.models import Fase


class NuevaFaseForm(forms.ModelForm):
    def __init__(self,*args,proyecto=None,**kwargs):
        super(NuevaFaseForm, self).__init__(*args,**kwargs)
        self.fields['fase_anterior'].queryset=Fase.objects.all().filter(proyecto=proyecto)
        self.fields['fase_anterior'].required=False

    class Meta:
        model = Fase
        fields = ['nombre', 'descripcion', 'fase_anterior']