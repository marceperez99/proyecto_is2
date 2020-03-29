from django import forms
from gestion_de_fase.models import Fase


class FaseForm(forms.ModelForm):
    """
    Form que se usa para la creacion de una fase.

    Clase Padre: forms.ModelForm

    """

    def __init__(self,*args,proyecto=None,**kwargs):
        """
            Metodo que se usa para incluir solo las fases del proyecto en donde se trabaja

            Args:

        """
        super(FaseForm, self).__init__(*args,**kwargs)
        self.fields['fase_anterior'].required=False
        if 'instace' in kwargs.keys():
            self.fields['fase_anterior'].queryset=Fase.objects.all().filter(proyecto=proyecto).exclude(id=kwargs['instance'].id)
        else:
            self.fields['fase_anterior'].queryset = Fase.objects.all().filter(proyecto=proyecto)

    class Meta:
        model = Fase
        fields = ['nombre', 'descripcion', 'fase_anterior']

