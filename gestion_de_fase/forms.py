from django import forms

from gestion_de_fase.models import Fase


class FaseForm(forms.ModelForm):
    """
    Form que permite crear y editar una fase.
    Es necesario espesificar la fase anterior al momento de crear una nueva fase, si no, esta se agregara como la primera fase

    Campos:
        -nombre: str, nombre de la fase
        -descripcion: str, descripcion de la nueva fase
        -fase anterior: Fase, fase anterior a la fase que se crea o se edita

    """
    descripcion = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))

    def __init__(self, *args, proyecto=None, **kwargs):
        """
        Constructor de la clase FaseForm.
        Para seleccionar la fase anterior posible, se filtra las fases por el proyecto que se paso como argumento.


        Argumentos:
            proyecto: Proyecto, en donde se creara o editara la nueva fase
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
