from django import forms
from gestion_de_item.models import Item, EstadoDeItem
from gestion_de_fase.models import Fase
from gestion_de_proyecto.models import Participante, Proyecto
from gestion_linea_base.utils import *


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
    razon_rompimiento = forms.CharField(label='Descripción del motivo de rompimiento',
                                        widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))


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
        self.fields['nombre'] = forms.CharField(initial=create_nombre_LB(proyecto=proyecto, fase=fase)
                                                , disabled=True, required=False)
        self.fields['items'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[(i.id, i.version.nombre) for i in Item.objects.filter(
                estado=EstadoDeItem.APROBADO,
                tipo_de_item__fase=fase)],
            label='Items'
        )

