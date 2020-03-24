from django import forms
from roles_de_sistema.models import RolDeSistema


class AsignarRolDeProyectoForm(forms.Form):

    def __init__(self, *args, usuario=None, **kwargs):
        super(AsignarRolDeProyectoForm, self).__init__(*args, **kwargs)
        self.usuario = usuario
        self.fields['Rol'] = forms.ChoiceField(choices=[(p.id, p.nombre) for p in RolDeSistema.objects.all()])
