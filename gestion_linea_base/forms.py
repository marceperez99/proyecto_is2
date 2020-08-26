from django import forms
from .models import LineaBase
from gestion_de_item.models import Item, EstadoDeItem


class LineaBaseForm(forms.ModelForm):
    """
    Form que permite la creacion de una nueva Linea Base.
    Los items a agreagar solo pudeden estar en estado "Aprobado".

    Campos:
        -items: blablala
    """

    class Meta:
        model = LineaBase
        fields = ('nombre', 'items',)

    def __init__(self, *args, proyecto=None, fase=None, **kwargs):
        """
        Constructor de la clase ProyectoForm.
        Para el posible gerente, el usuario seleciona entre los usuarios logeados un gerente
        """

        super(LineaBaseForm, self).__init__(*args, **kwargs)
        self.fields['nombre'] = forms.CharField(initial=LineaBase.create_nombre(self=None, proyecto=proyecto, fase=fase)
                                                , disabled=True, required=False)
        self.fields['items'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[(i.id, i.version.nombre) for i in Item.objects.filter(
                estado=EstadoDeItem.APROBADO,
                tipo_de_item__fase__proyecto_id=proyecto.id)],
            label='Items'
        )
