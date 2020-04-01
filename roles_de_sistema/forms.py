from django import forms
from django.contrib.auth.models import Permission

from .models import RolDeSistema

class NewRolDeSistemaForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(NewRolDeSistemaForm, self).__init__(*args, **kwargs)
        self.fields['permisos'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=[ (p.id,p.name) for p in Permission.objects.all() if p.codename.startswith('ps_')])

    class Meta:
        model = RolDeSistema
        fields = ['nombre','descripcion','permisos']