from django import forms

from gestion_de_fase.models import Fase


class FaseForm(forms.ModelForm):
    """
    Form que se usa para la creacion de una fase.

    Clase Padre:
        forms.ModelForm
    """
    descripcion = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))

    def __init__(self, *args, proyecto=None, **kwargs):
        """
        Constructor del form, recibe los datos de la fase y la fase anterior

        Argumentos:
            proyecto: Proyecto
        """
        super(FaseForm, self).__init__(*args, **kwargs)
        self.fields['fase_anterior'].required = False
        if 'instace' in kwargs.keys():
            self.fields['fase_anterior'].queryset = Fase.objects.all().filter(proyecto=proyecto).exclude(
                id=kwargs['instance'].id)
        else:
            self.fields['fase_anterior'].queryset = Fase.objects.all().filter(proyecto=proyecto)
            self.fields['fase_anterior'].empty_label = 'Seleccione una Fase'

    class Meta:
        model = Fase
        fields = ['nombre', 'descripcion', 'fase_anterior']
        help_texts = {'fase_anterior': 'Indique tras qué fase del Proyecto se desarrollará esta nueva fase.'}
