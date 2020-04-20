from django import forms
from django.contrib.auth.models import Permission
from .models import RolDeProyecto


class NewRolDeProyectoForm(forms.ModelForm):
    """
    Formulario utilizado para crear un nuevo rol de Proyecto.

    Este formulario esta basado en el Modelo RolDeProyecto.

    Clase Padre:
        form.ModelForm
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor del Formulario.

        Agrega, en el campo 'permisos', los Permisos de Proyecto que podrá tener el rol.
        """
        super(NewRolDeProyectoForm, self).__init__(*args, **kwargs)
        self.fields['permisos'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                            choices=[(p.id, p.name) for p in Permission.objects.all() if
                                                                     p.codename.startswith('pp_')])

    class Meta:
        model = RolDeProyecto
        fields = ['nombre', 'descripcion', 'permisos']
