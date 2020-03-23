from django import forms
from django.contrib.auth.models import Permission

from .models import RolDeSistema
class NewRolDeSistemaForm(forms.ModelForm):
    class Meta:
        model = RolDeSistema
        fields = ['nombre','descripcion','permisos']