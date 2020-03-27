from django import forms
from gestion_de_fase.models import Fase


class NuevaFaseForm(forms.ModelForm):
    """
    Form que se usa para la creacion de una fase.

    Clase Padre: forms.ModelForm

    """

    def __init__(self,*args,proyecto=None,**kwargs):
        """
            Metodo que se usa para incluir solo las fases del proyecto en donde se trabaja

            Args:

        """
        super(NuevaFaseForm, self).__init__(*args,**kwargs)
        self.fields['fase_anterior'].queryset=Fase.objects.all().filter(proyecto=proyecto)
        self.fields['fase_anterior'].required=False

    class Meta:
        model = Fase
        fields = ['nombre', 'descripcion', 'fase_anterior']