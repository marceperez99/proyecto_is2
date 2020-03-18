from django import forms
from django.contrib.auth.models import Permission

from .models import RolDeProyecto
class NewRolDeProyectoForm(forms.ModelForm):
    permisos = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=[ (p.id,p.name) for p in Permission.objects.all() if p.codename.startswith('pp_')])
    class Meta:
        model = RolDeProyecto
        fields = ['nombre','descripcion','permisos']