from django import forms

from roles_de_sistema.models import RolDeSistema


class AsignarRolDeSistemaForm(forms.Form):
    """
    Formulario utilizado para asignar  un rol de Sistema a un Usuario.

    Clase Padre:
        form.ModelForm
    """

    def __init__(self, *args, usuario=None, **kwargs):
        """
        Constructor del Formulario.

        Agrega, en el campo 'Rol', los Roles de Sistema que el Usuario podrá tener.
        """
        super(AsignarRolDeSistemaForm, self).__init__(*args, **kwargs)
        self.usuario = usuario
        self.fields['Rol'] = forms.ChoiceField(choices=[(p.id, p.nombre) for p in RolDeSistema.objects.all()])


class ConfigCloudForm(forms.Form):
    """
    Formulario utilizado para escribir en el archivo json de donde se leerán las configuraciones para conectarse a la
    nube, dichas configuraciones

    Clase Padre:
        form.ModelForm
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor del Formulario.

        Agrega un campo TextArea para escribir en él las configuraciones del json
        """
        super(ConfigCloudForm, self).__init__(*args, **kwargs)
        self.fields['Json de Configuración del Cloud'] = forms.CharField(widget=forms.Textarea)
