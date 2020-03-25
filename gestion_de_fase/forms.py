from django import forms
from gestion_de_fase.models import Fase


class NuevaFaseForm(forms.ModelForm):
    """
    Form que se usa para la creacion de una fase, se usan solo las fases del proyecto en donde se trabaja

    Clase Padre: forms.ModelForm

    Agrs:

        nombre: models.CharField

        descripcion: models.CharField

        fase_anterior: models.ForeignKey
    """

    def __init__(self,*args,proyecto=None,**kwargs):
        super(NuevaFaseForm, self).__init__(*args,**kwargs)
        self.fields['fase_anterior'].queryset=Fase.objects.all().filter(proyecto=proyecto)
        self.fields['fase_anterior'].required=False

    class Meta:
        model = Fase
        fields = ['nombre', 'descripcion', 'fase_anterior']