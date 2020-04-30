from django import forms

from roles_de_sistema.models import RolDeSistema


class AsignarRolDeSistemaForm(forms.Form):

    def __init__(self, *args, usuario=None, **kwargs):
        super(AsignarRolDeSistemaForm, self).__init__(*args, **kwargs)
        self.usuario = usuario
        self.fields['Rol'] = forms.ChoiceField(choices=[(p.id, p.nombre) for p in RolDeSistema.objects.all()])


class ConfigCloudForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ConfigCloudForm, self).__init__(*args, **kwargs)
        self.fields['Json de Configuración del Cloud'] = forms.CharField(widget=forms.Textarea)
